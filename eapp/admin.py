from django.contrib import admin
from .models import Cart, Product, CartProduct, Category, Customer, Order, Admin


admin.site.register(Admin),
admin.site.register(Category),
admin.site.register(Product),
admin.site.register(Cart),
admin.site.register(CartProduct),
admin.site.register(Order),



