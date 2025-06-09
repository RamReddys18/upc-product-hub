
from django.contrib import admin
from .models import Product, Category, Size, ProductAttribute, EditLog

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'upc', 'brand_name', 'status', 'submitted_by', 'created_at']
    list_filter = ['status', 'category', 'size', 'created_at']
    search_fields = ['name', 'upc', 'brand_name']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']

@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']

@admin.register(ProductAttribute)
class ProductAttributeAdmin(admin.ModelAdmin):
    list_display = ['product', 'key', 'value']
    list_filter = ['key']

@admin.register(EditLog)
class EditLogAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'action', 'timestamp']
    list_filter = ['action', 'timestamp']
    readonly_fields = ['timestamp']
