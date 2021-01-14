from django.conf import settings
from django.db import models
from django.db.models import Sum
from django.shortcuts import reverse,redirect
from django_countries.fields import CountryField

# Create your models here.
class Categories(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.title


CATEGORY_CHOICES =(
    ('TS', 'Tee shirt'),
    ('MW','Mens Wear'),
    ('LW','Ladies Wear'),

)

LABEL_CHOICES =(
    ('P', 'primary'),
    ('S','secondary'),
    ('D','danger'),

)
class Item(models.Model):

    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='products')
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null=True)
    category = models.ForeignKey(Categories,on_delete=models.CASCADE)
    label = models.CharField(choices=LABEL_CHOICES, max_length=1)
    slug = models.SlugField()
    description = models.TextField()


    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("vest_v3:product-page", kwargs={
            'slug': self.slug
        })

    def get_add_to_cart_url(self):
        return reverse("vest_v3:add-to-cart", kwargs={
            'slug': self.slug
        })
    def get_remove_from_cart_url(self):
        return reverse("vest_v3:remove-from-cart", kwargs={
            'slug': self.slug
        })

class ProductImage(models.Model):
    product = models.ForeignKey(Item, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/images')

    def __str__(self):
        return self.product.title



class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,blank=True, null=True)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.item.title}"

    def get_total_item_price(self):
        return self.quantity * self.item.price

    def get_total_discount_price(self):
        return self.quantity * self.item.discount_price

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_price()

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_price()
        return self.get_total_item_price()


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem)
    started = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    billing_address = models.ForeignKey('BillingAddress', on_delete=models.SET_NULL, blank=True, null=True)
    payment = models.ForeignKey('Payment', on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.user.username

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        return total

class BillingAddress(models.Model):
    user =  models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=10)
    last_name = models.CharField(max_length=10)
    street_address = models.CharField(max_length=40)
    appartment_address = models.CharField(max_length=40)
    country = CountryField(multiple=False)
    state = CountryField(multiple=False)
    district = CountryField(multiple=False)
    pincode = models.CharField(max_length=6)
    contact = models.CharField(max_length=10)
    alternate_contact = models.CharField(max_length=10)


    def __str__(self):
        return self.user.username

class Payment(models.Model):
    pass