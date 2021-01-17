from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget

PAYMENT_CHOICES = (
    ('S','Stripe'),
    ('P', 'Paypal'),
)

class CheckoutForm(forms.Form):
    shipping_first_name = forms.CharField( required=True, widget=forms.TextInput(attrs={
        'class' : 'form-control'
    }))
    shipping_last_name = forms.CharField( required=True, widget=forms.TextInput(attrs={
        'class' : 'form-control'
    }))

    shipping_address1 = forms.CharField(required=False ,widget=forms.TextInput(attrs={
        'placeholder' : 'Door no. or Appartment name',
        'class': 'form-control'
    }))
    shipping_address2 = forms.CharField( required=False,widget=forms.TextInput(attrs={
        'placeholder' : 'Street address',
        'class': 'form-control'
    }))
    shipping_country = CountryField(blank_label ='(select Country)').formfield(widget=CountrySelectWidget(attrs={
        'class':'custom-select d-block w-100'
    }) )
    shipping_state = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Street address',
        'class': 'form-control'
    }))
    shipping_district = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Street address',
        'class': 'form-control'
    }))
    shipping_pincode = forms.IntegerField(required=False, widget=forms.TextInput(attrs={
        'class' : 'form-control'
    }))
    shipping_contact = forms.IntegerField(widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))
    shipping_alternate_contact = forms.IntegerField(widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))

    billing_address = forms.CharField(required=False)
    billing_first_name = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))
    billing_last_name = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))
    billing_address1 = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Door no. or Appartment name',
        'class': 'form-control'
    }))
    billing_address2 = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Street address',
        'class': 'form-control'
    }))
    billing_country = CountryField(blank_label='(select Country)').formfield(widget=CountrySelectWidget(attrs={
        'class': 'custom-select d-block w-100'
    }))
    billing_state = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Street address',
        'class': 'form-control'
    }))
    billing_district = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Street address',
        'class': 'form-control'
    }))
    billing_pincode = forms.IntegerField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))
    billing_contact = forms.IntegerField(widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))
    billing_alternate_contact = forms.IntegerField(widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))


    #contact = forms.IntegerField( widget=forms.TextInput(attrs={
     #   'class' : 'form-control'
    #}))
    #alternate_contact = forms.IntegerField( widget=forms.TextInput(attrs={
     #   'class' : 'form-control'
    #}))
    #same_shipping_address = forms.BooleanField(required=False,widget=forms.TextInput(attrs={
    #    'class' : 'custom-control-input'
    #}))
    #save_info = forms.BooleanField(required=False,widget=forms.TextInput(attrs={
    #    'class' : 'custom-control-input'
    #}))

    #this is for selecting options
    same_billing_address = forms.BooleanField(required=False)
    set_default_shipping = forms.BooleanField(required=False)
    use_default_shipping = forms.BooleanField(required=False)
    set_default_billing = forms.BooleanField(required=False)
    use_default_billing = forms.BooleanField(required=False)

    payment_option = forms.ChoiceField(widget=forms.RadioSelect, choices=PAYMENT_CHOICES)



class CouponForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Promo code',
        'aria-label': 'Recipient\'s username',
        'aria-describedby': 'basic-addon2'
    }))


class RefundForm(forms.Form):
    ref_code = forms.CharField()
    message = forms.CharField(widget=forms.Textarea(attrs={
        'rows': 4
    }))
    email = forms.EmailField()


class PaymentForm(forms.Form):
    stripeToken = forms.CharField(required=False)
    save = forms.BooleanField(required=False)
    use_default = forms.BooleanField(required=False)