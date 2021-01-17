from django.shortcuts import render, get_object_or_404,redirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.core.mail import EmailMessage
from .forms import *
from django.contrib import messages
from django.conf import settings
from django.views.generic import DetailView, ListView,View,TemplateView
from django.db.models import F
from django.utils import timezone
from .models import *
import stripe
import razorpay
import random
import string


stripe.api_key = "sk_test_4eC39HqLyjWDarjtT1zdp7dc" #settings.STRIPE_SECRET_KEY

# `source` is obtained with Stripe.js; see https://stripe.com/docs/payments/accept-a-payment-charges#web-create-token

def create_ref_code():
    return 'VF_21_'.join(random.choices(string.ascii_lowercase + string.digits, k=14))

def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid


# Create your views here.

class HomeView(ListView):
    model = Item
    paginate_by = 10
    template_name = 'home-page.html'

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
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            form = CheckoutForm()
            context = {
                'form': form,
                'couponform': CouponForm(),
                'order': order,
                'DISPLAY_COUPON_FORM': True
            }

            shipping_address_qs = Address.objects.filter(
                user=self.request.user,
                address_type='S',
                default=True
            )
            if shipping_address_qs.exists():
                context.update(
                    {'default_shipping_address': shipping_address_qs[0]})

            billing_address_qs = Address.objects.filter(
                user=self.request.user,
                address_type='B',
                default=True
            )
            if billing_address_qs.exists():
                context.update(
                    {'default_billing_address': billing_address_qs[0]})
            return render(self.request, "checkout-page.html", context)
        except ObjectDoesNotExist:
            messages.info(self.request, "You do not have an active order")
            return redirect("vest_v3:checkout-page")



    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)

        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():

                use_default_shipping = form.cleaned_data.get(
                    'use_default_shipping')
                if use_default_shipping:
                    print("Using the defualt shipping address")
                    address_qs = Address.objects.filter(
                        user=self.request.user,
                        address_type='S',
                        default=True
                    )
                    if address_qs.exists():
                        shipping_address = address_qs[0]
                        order.shipping_address = shipping_address
                        order.save()
                    else:
                        messages.info(
                            self.request, "No default shipping address available")
                        return redirect('core:checkout')
                else:
                    print("User is entering a new shipping address")
                    shipping_first_name = form.cleaned_data.get('first_name')
                    shipping_last_name = form.cleaned_data.get('last_name')
                    shipping_address1 = form.cleaned_data.get('street_address')
                    shipping_address2 = form.cleaned_data.get('appartment_address')
                    shipping_country = form.cleaned_data.get('country')
                    shipping_state = form.cleaned_data.get('state')
                    shipping_district = form.cleaned_data.get('district')
                    shipping_pincode = form.cleaned_data.get('pincode')
                    shipping_contact = form.cleaned_data.get('contact')
                    shipping_alternate_contact = form.cleaned_data.get('alternate_contact')

                    if is_valid_form([shipping_first_name, shipping_last_name, shipping_address1,
                                      shipping_address2,shipping_country,shipping_state,
                                      shipping_district,shipping_pincode,shipping_contact,shipping_alternate_contact]):
                        shipping_address = Address(

                            user=self.request.user,
                            first_name=shipping_first_name,
                            last_name=shipping_last_name,
                            street_address=shipping_address1,
                            apartment_address=shipping_address2,
                            country=shipping_country,
                            district=shipping_district,
                            pincode=shipping_pincode,
                            contact=shipping_contact,
                            alternate_contact=shipping_alternate_contact,
                            address_type='S'
                        )
                        shipping_address.save()

                        order.shipping_address = shipping_address
                        order.save()

                        set_default_shipping = form.cleaned_data.get('set_default_shipping')
                        if set_default_shipping:
                            shipping_address.default = True
                            shipping_address.save()

                    else:
                        messages.info(self.request, "Please fill in the required shipping address fields")

                use_default_billing = form.cleaned_data.get('use_default_billing')
                same_billing_address = form.cleaned_data.get('same_billing_address')

                if same_billing_address:
                    billing_address = shipping_address
                    billing_address.pk = None
                    billing_address.save()
                    billing_address.address_type = 'B'
                    billing_address.save()
                    order.billing_address = billing_address
                    order.save()

                elif use_default_billing:
                    print("Using the defualt billing address")
                    address_qs = Address.objects.filter(
                        user=self.request.user,
                        address_type='B',
                        default=True
                    )
                    if address_qs.exists():
                        billing_address = address_qs[0]
                        order.billing_address = billing_address
                        order.save()
                    else:
                        messages.info(
                            self.request, "No default billing address available")
                        return redirect('vest_v3:checkout')
                else:
                    print("User is entering a new billing address")
                    billing_first_name = form.cleaned_data.get('first_name')
                    billing_last_name = form.cleaned_data.get('last_name')
                    billing_address1 = form.cleaned_data.get('street_address')
                    billing_address2 = form.cleaned_data.get('appartment_address')
                    billing_country = form.cleaned_data.get('country')
                    billing_state = form.cleaned_data.get('state')
                    billing_district = form.cleaned_data.get('district')
                    billing_pincode = form.cleaned_data.get('pincode')
                    billing_contact = form.cleaned_data.get('contact')
                    billing_alternate_contact = form.cleaned_data.get('alternate_contact')

                    if is_valid_form([billing_first_name, billing_last_name, billing_address1,
                                      billing_address2, billing_country, billing_state,
                                      billing_district, billing_pincode, billing_contact,
                                      billing_alternate_contact]):
                        billing_address = Address(

                            user=self.request.user,
                            first_name=billing_first_name,
                            last_name=billing_last_name,
                            street_address=billing_address1,
                            apartment_address=billing_address2,
                            country=billing_country,
                            district=billing_district,
                            pincode=billing_pincode,
                            contact=billing_contact,
                            alternate_contact=billing_alternate_contact,
                            address_type='B'
                        )
                        billing_address.save()

                order.billing_address = billing_address
                order.save()

                set_default_billing = form.cleaned_data.get(
                    'set_default_billing')
                if set_default_billing:
                    billing_address.default = True
                    billing_address.save()

            else:
                messages.info(
                    self.request, "Please fill in the required billing address fields")

            if payment_option: # == 'S'
                return redirect('vest_v3:payment', payment_option='stripe')
            #elif payment_option == 'P':
             #   return redirect('vest_v3:payment', payment_option='paypal')
            else:
                messages.warning(
                    self.request, "Invalid payment option selected")
                return redirect('vest_v3:checkout-page')
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("vest_v3:order-summary")



#To handle payments from checkout view
class PaymentView(View):
    def get(self, request, *args, **kwargs):
        order = Order.objects.get(user=request.user, ordered=False)
        if order.billing_address:
            context = {
                'order': order,
                'DISPLAY_COUPON_FORM': False,
                'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY
            }
            userprofile = self.request.user.userprofile
            if userprofile.one_click_purchasing:
                # fetch the users card list
                cards = stripe.Customer.list_sources(
                    userprofile.stripe_customer_id,
                    limit=3,
                    object='card'
                )
                card_list = cards['data']
                if len(card_list) > 0:
                    # update the context with the default card
                    context.update({
                        'card': card_list[0]
                    })
            return render(self.request, "payment.html", context)
        else:
            messages.warning(
                self.request, "You have not added a billing address")
            return redirect("vest_v3:checkout-page")

    def post(self, request, *args, **kwargs):
        order = Order.objects.get(user = request.user, ordered = False)
        form = PaymentForm(self.request.POST)
        userprofile = UserProfile.objects.get(user=self.request.user)
        if form.is_valid():
            token = form.cleaned_data.get('stripeToken')
            save = form.cleaned_data.get('save')
            use_default = form.cleaned_data.get('use_default')

            if save:
                if userprofile.stripe_customer_id != '' and userprofile.stripe_customer_id is not None:
                    customer = stripe.Customer.retrieve(
                        userprofile.stripe_customer_id)
                    customer.sources.create(source=token)

                else:
                    customer = stripe.Customer.create(
                        email=self.request.user.email,
                    )
                    customer.sources.create(source=token)
                    userprofile.stripe_customer_id = customer['id']
                    userprofile.one_click_purchasing = True
                    userprofile.save()

            amount = int(order.get_total() * 100)

            try:
                if use_default or save:
                    # charge the customer because we cannot charge the token more than once
                    charge = stripe.Charge.create(
                        amount=amount,  # cents
                        currency="usd",
                        customer=userprofile.stripe_customer_id
                    )
                else:
                    # charge once off on the token
                    charge = stripe.Charge.create(
                        amount=amount,  # cents
                        currency="usd",
                        source=token
                    )

                # payments
                payment = Payment()
                payment.stripe_charge_id = charge['id']
                payment.user = request.user
                payment.amount = order.get_total()
                payment.save()

                # assign payment to the order
                order_items = order.items.all()
                order_items.update(ordered=True)
                for item in order_items:
                    item.save()

                order.ordered = True
                order.payment = payment
                order.ref_code = create_ref_code()
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

        messages.warning(self.request, "Invalid data received")
        return redirect("/payment/stripe/")
#razorpay
#client = razorpay.Client(auth = ('<key_id>', '<key_secret>'))
#params_dict = {
#    'order_id': '12122',
#    'razorpay_payment_id': '332',
#    'razorpay_signature': '23233'
#}
#client.utility.verify_payment_signature(params_dict)

#General View
def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        messages.info(request, "This coupon does not exist")
        return redirect("vest_v3:checkout")

class AddCouponView(View):
    def post(self, *args, **kwargs):
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order = Order.objects.get(
                    user=self.request.user, ordered=False)
                order.coupon = get_coupon(self.request, code)
                order.save()
                messages.success(self.request, "Successfully added coupon")
                return redirect("vest_v3:checkout")
            except ObjectDoesNotExist:
                messages.info(self.request, "You do not have an active order")
                return redirect("vest_v3:checkout")

class RequestRefundView(View):
    def get(self, *args, **kwargs):
        form = RefundForm()
        context = {
            'form': form
        }
        return render(self.request, "request_refund.html", context)

    def post(self, *args, **kwargs):
        form = RefundForm(self.request.POST)
        if form.is_valid():
            ref_code = form.cleaned_data.get('ref_code')
            message = form.cleaned_data.get('message')
            email = form.cleaned_data.get('email')
            # edit the order
            try:
                order = Order.objects.get(ref_code=ref_code)
                order.refund_requested = True
                order.save()

                # store the refund
                refund = Refund()
                refund.order = order
                refund.reason = message
                refund.email = email
                refund.save()

                messages.info(self.request, "Your request was received.")
                return redirect("vest_v3:request-refund")

            except ObjectDoesNotExist:
                messages.info(self.request, "This order does not exist.")
                return redirect("vest_v3:request-refund")


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


#2ndtype
def sendmail(request):
    if request.method == 'POST':
        name = request.POST['sender']
        emailsender = request.POST['email']
        message = request.POST['message']
        subject = f'Message from {name}'
        try:
            email = EmailMessage(
                subject,
                message,
                'loges20@gmail.com',
                ['care@vfind.in'],
                reply_to=[emailsender],
                fail_silently = False
            )
            email.send()
            messages.success(request, 'Email Sent')
            print('Mail Sent')
            return HttpResponseRedirect(reverse('mail'))
        except:
            messages.error(request, 'Email not Sent')
            return HttpResponseRedirect(reverse('mail'))
    return render(request, 'mail.html')

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

class ItemDetailView(DetailView):
    model = Item
    template_name = 'product-page.html'





