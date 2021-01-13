from django.urls import path
from .views import *
from . import views

app_name = 'vest_v3'

urlpatterns = [

    path('',HomeView.as_view(), name='home-page'),
    path('product/<slug>',ItemDetailView.as_view(), name='product-page'),
    path('checkout/',CheckoutView.as_view(), name='checkout-page'),
    path('categories/', CategoryView.as_view(), name='categories'),
    path('add-to-cart/<slug>/',views.add_to_cart,name='add-to-cart'),
    path('order-summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('remove-from-cart/<slug>/',views.remove_from_cart,name='remove-from-cart'),
    path('remove-single-item-cart/<slug>/',views.remove_single_item_cart,name='remove-single-item-cart'),
    path('add-single-item-to-cart/<slug>/',views.add_single_item_to_cart,name='add-single-item-to-cart'),
    path('payment/',PaymentView.as_view(),name='payment'),#<payment_option>/



#general
    path('trackshipping/', TrackShippingView.as_view(), name='trackshipping'),
    path('privacypolicy/',PrivacyPolicyView.as_view(), name='privacypolicy'),
    path('retexc/',RetexcView.as_view(), name='retexc'),
    path('shippingpolicy/',ShippingPolicyView.as_view(), name='shippingpolicy'),
    path('termsandconditions/',TermsandConditionsView.as_view(), name='termsandconditions'),
    path('contact/', views.contact, name='contact'),
    path('offer-page/', OfferPageView.as_view(), name='offer-page'),

]