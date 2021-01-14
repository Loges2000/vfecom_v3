from django.shortcuts import render, get_object_or_404,redirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import *
from django.contrib import messages
from django.conf import settings
from django.views.generic import DetailView, ListView,View,TemplateView
from django.db.models import F
from django.utils import timezone
from .models import *
import stripe
import razorpay


stripe.api_key = "sk_test_4eC39HqLyjWDarjtT1zdp7dc" #settings.STRIPE_SECRET_KEY

# `source` is obtained with Stripe.js; see https://stripe.com/docs/payments/accept-a-payment-charges#web-create-token




# Create your views here.

class HomeView(ListView):
    model = Item
    paginate_by = 10
    template_name = 'home-page.html'

class ItemDetailView(DetailView):
    model = Item
    template_name = 'product-page.html'

class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, 'ordersummary.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("/")

class CategoryView(ListView):
    model = Categories
    template_name = 'categories.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['allcategories'] = Categories.objects.all()
        return context


#adding to cart
@login_required
def add_to_cart(request,slug):
    item = get_object_or_404(Item,slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user = request.user,
        ordered = False
    )
    order_qs = Order.objects.filter(user = request.user, ordered = False)

    if order_qs.exists():
        order = order_qs[0]
        #check if the order item is in the order
        if order.items.filter(item__slug = item.slug).exists():
            #order_item.quantity += 1
            order_item.quantity = F('quantity') + 1  #if  This is okay until 2 people click "Add to cart" at the same time or a user clicks very fast that the first request isn't finished, This is a race condition and should be avoided. Like this
            order_item.save()
            messages.info(request,"Quantity updated to your cart")
            return redirect('vest_v3:product-page', slug=slug)
        else:
            order.items.add(order_item)
            messages.info(request, "This item added to your cart")
            return redirect('vest_v3:product-page', slug=slug)
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user = request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request,"This item added to your cart")
        return redirect('vest_v3:product-page',slug = slug)

#removing item from cart
@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)

    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user = request.user,
                ordered = False
            )[0]
            order.items.remove(order_item)
            messages.info(request,"This item removed from your cart")
            return redirect("vest_v3:order-summary")
        else:
            messages.info(request, "This Item was not in your cart")
            return redirect('vest_v3:product-page', slug=slug)

    else:
        messages.info(request,"You do not have active order!!")
        return redirect("vest_v3:product-page",slug = slug)




#function removing single item in cart
@login_required
def remove_single_item_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)

    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user = request.user,
                ordered = False
            )[0]
            if order_item.quantity >1:
                order_item.quantity = F(
                    'quantity') - 1  # if  This is okay until 2 people click "Add to cart" at the same time or a user clicks very fast that the first request isn't finished, This is a race condition and should be avoided. Like this
                order_item.save()
            else:

                order.items.remove(order_item)



            messages.info(request,"The item quantity is updated")
            return redirect("vest_v3:order-summary")
        else:
            messages.info(request, "This Item was not in your cart")
            return redirect('vest_v3:order-summary', slug=slug)

    else:
        messages.info(request,"You do not have active order!!")
        return redirect("vest_v3:order-summary",slug = slug)

#function adding singleitem in cart
@login_required
def add_single_item_to_cart(request,slug):
    item = get_object_or_404(Item,slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user = request.user,
        ordered = False
    )
    order_qs = Order.objects.filter(user = request.user, ordered = False)

    if order_qs.exists():
        order = order_qs[0]
        #check if the order item is in the order
        if order.items.filter(item__slug = item.slug).exists():
            #order_item.quantity += 1
            order_item.quantity = F('quantity') + 1  #if  This is okay until 2 people click "Add to cart" at the same time or a user clicks very fast that the first request isn't finished, This is a race condition and should be avoided. Like this
            order_item.save()
            messages.info(request,"The item quantity added in your cart")
            return redirect('vest_v3:order-summary')
        else:
            order.items.add(order_item)
            messages.info(request, "This item added to your cart")
            return redirect('vest_v3:order-summary',slug = slug)
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user = request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request,"This item added to your cart")
        return redirect('vest_v3:order-summary',slug = slug)







class CheckoutView(View):
    def get(self, *args,**kwargs):
        form = CheckoutForm()
        context = {
            'form':form
        }
        return render(self.request, 'checkout-page.html', context)

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)

        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                first_name = form.cleaned_data.get('first_name')
                last_name = form.cleaned_data.get('last_name')
                street_address = form.cleaned_data.get('street_address')
                appartment_address = form.cleaned_data.get('appartment_address')
                country = form.cleaned_data.get('country')
                state = form.cleaned_data.get('state')
                district = form.cleaned_data.get('district')
                pincode = form.cleaned_data.get('pincode')
                contact = form.cleaned_data.get('contact')
                alternate_contact = form.cleaned_data.get('alternate_contact')
                #TODO : need to add more functionality
                #same_shipping_address = form.cleaned_data.get('same_shipping_address')
                #save_info = form.cleaned_data.get('save_info')
                payment_option = form.cleaned_data.get('payment_option')
                print(form.cleaned_data)
                print('the form is valid')

                billing_address = BillingAddress(
                    user=self.request.user,
                    first_name=first_name,
                    last_name=last_name,
                    street_address=street_address,
                    appartment_address=appartment_address,
                    country=country,
                    state=state,
                    district=district,
                    pincode=pincode,
                    contact=contact,
                    alternate_contact=alternate_contact
                )
                billing_address.save()
                order.billing_address = billing_address
                order.save()
                #TODO: need to redirect to selected payment options
                return redirect('vest_v3:checkout-page')
            messages.warning(self.request, "Checkout Failed")
            return redirect('vest_v3:checkout-page')

        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an active order")
            return redirect("vest_v3:order-summary")

        print(self.request.POST)


#To handle payments from checkout view
class PaymentView(View):
    def get(self, request, *args, **kwargs):
        order = Order.objects.get(user=request.user, ordered=False)
        context = {
            'order': order
        }
        return render(request, 'payment.html', context)

    def post(self, request, *args, **kwargs):
        order = Order.objects.get(user = request.user, ordered = False)
        amount = int(order.get_total() * 100)
        token = request.POST.get('StripeToken')

        try:
            charge = stripe.Charge.create(
                amount=amount,
                currency="inr",
                source=token,
            )

            # payments
            payment = Payment()
            payment.stripe_charge_id = charge['id']
            payment.user = request.user
            payment.amount = order.get_total()
            payment.save()

            # assign payment to the order
            order.ordered = True
            order.payment = payment
            order.save()

            messages.success(request, "your order was succesful")
            return redirect('/')

        except stripe.error.CardError as e:
            # Since it's a decline, stripe.error.CardError will be caught
            body = e.json_body
            err = body.get('error',{})

            messages.error(request, f"{err.get('message')}")
            return redirect('/')

        except stripe.error.RateLimitError as e:
            messages.error(request, "Rate Limit Error")
            return redirect('/')

        except stripe.error.InvalidRequestError as e:
           messages.error(request, "Invalid Parameters")
           return redirect('/')

        except stripe.error.AuthenticationError as e:
            messages.error(request, "Not Authenticated")
            return redirect('/')


        except stripe.error.APIConnectionError as e:
            messages.error(request, "Network Error")
            return redirect('/')


        except stripe.error.StripeError as e:
            messages.error(request, "Something went wrong, you are not charged.Please try again!")
            return redirect('/')


        except Exception as e:
            messages.error(request,"Critical error, we have been notified")
            return redirect('/')

#razorpay
#client = razorpay.Client(auth = ('<key_id>', '<key_secret>'))
#params_dict = {
#    'order_id': '12122',
#    'razorpay_payment_id': '332',
#    'razorpay_signature': '23233'
#}
#client.utility.verify_payment_signature(params_dict)

def home(request):
    context = {
        'items': Item.objects.all()
    }
    return render(request,'home-page.html',context)

def products(request):
    context = {
        'items' : Item.objects.all()
    }
    return render(request,'product-page.html',context)

def checkout(request):

    return render(request,'checkout-page.html')

def categories(request):

    return render(request,'categories.html')









#General View


def contact(request):
    if request.method == 'POST':
        message_name = request.POST['message-name']
        message_email = request.POST['message-email']
        mobile_no = request.POST['mobile-no']
        company = request.POSt['company']
        message = request.POST['message']

        #send email
        send_mail(
            message_name,
            message_email,
            mobile_no,
            company,
            message,
            ['loges20@gmail.com','care@vfind.in'],
            fail_silently=False

        )
        return render(request,'general/contact.html',{'message_name': message_name})
    else:
        return render(request,'general/contact.html', {})


class TrackShippingView(TemplateView):
    template_name = 'general/trackshipping.html'



class PrivacyPolicyView(TemplateView):
    template_name = 'general/privacypolicy.html'

class RetexcView(TemplateView):
    template_name = 'general/retexc.html'

class ShippingPolicyView(TemplateView):
    template_name = 'general/shippingpolicy.html'

class TermsandConditionsView(TemplateView):
    template_name = 'general/termsandconditions.html'

class OfferPageView(TemplateView):
    template_name = 'offerpage.html'




