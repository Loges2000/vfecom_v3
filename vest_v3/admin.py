from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register([Order,Item,OrderItem, Categories,Payment,ProductImage])
