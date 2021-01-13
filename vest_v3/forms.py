from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget

PAYMENT_CHOICES = (
    ('S','Stripe'),
    ('P', 'Paypal'),
)

class CheckoutForm(forms.Form):
    first_name = forms.CharField( required=True, widget=forms.TextInput(attrs={
        'class' : 'form-control'
    }))
    last_name = forms.CharField( required=True, widget=forms.TextInput(attrs={
        'class' : 'form-control'
    }))
    street_address = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder' : 'Door no. or Appartment name',
        'class': 'form-control'
    }))
    appartment_address = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder' : 'Street address',
        'class': 'form-control'
    }))
    country = CountryField(blank_label ='(select Country)').formfield(widget=CountrySelectWidget(attrs={
        'class':'custom-select d-block w-100'
    }) )
    state = CountryField(blank_label ='(select State)').formfield(widget=CountrySelectWidget(attrs={
        'class':'custom-select d-block w-100'
    }) )
    district = CountryField(blank_label ='(select District)').formfield(widget=CountrySelectWidget(attrs={
        'class':'custom-select d-block w-100'
    }) )
    pincode = forms.IntegerField(widget=forms.TextInput(attrs={
        'class' : 'form-control'
    }))
    contact = forms.IntegerField( widget=forms.TextInput(attrs={
        'class' : 'form-control'
    }))
    alternate_contact = forms.IntegerField( widget=forms.TextInput(attrs={
        'class' : 'form-control'
    }))
    same_shipping_address = forms.BooleanField(required=False,widget=forms.TextInput(attrs={
        'class' : 'custom-control-input'
    }))
    save_info = forms.BooleanField(required=False,widget=forms.TextInput(attrs={
        'class' : 'custom-control-input'
    }))
    payment_option = forms.ChoiceField(widget=forms.RadioSelect, choices=PAYMENT_CHOICES)
