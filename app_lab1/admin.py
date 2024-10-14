from django.contrib import admin
from .models import Category, Product, CategoryProduct

# Регистрируем модели в админке
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(CategoryProduct)
