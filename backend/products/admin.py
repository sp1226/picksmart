# backend/products/admin.py
from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'price', 'theme', 'created_at']
    list_filter = ['theme']
    search_fields = ['title', 'description']
