
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Categories"

class Size(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class Product(models.Model):
    STATUS_CHOICES = [
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    # Basic product information
    name = models.CharField(max_length=255)
    upc = models.CharField(max_length=50, unique=True)
    ean = models.CharField(max_length=50, blank=True, null=True)
    brand_name = models.CharField(max_length=255)
    description = models.TextField()
    
    # Categorization
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    
    # Status and workflow
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='under_review')
    rejection_reason = models.TextField(blank=True, null=True)
    
    # User tracking
    submitted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submitted_products')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_products')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.name} ({self.upc})"
    
    def save(self, *args, **kwargs):
        # Convert UPC and EAN to uppercase
        if self.upc:
            self.upc = self.upc.upper()
        if self.ean:
            self.ean = self.ean.upper()
        # Convert brand name to title case
        if self.brand_name:
            self.brand_name = self.brand_name.title()
        super().save(*args, **kwargs)
    
    def can_edit(self, user):
        return self.submitted_by == user and self.status == 'rejected'
    
    class Meta:
        ordering = ['-created_at']

class ProductAttribute(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='attributes')
    key = models.CharField(max_length=100)
    value = models.CharField(max_length=255)
    
    def __str__(self):
        return f"{self.key}: {self.value}"
    
    class Meta:
        unique_together = ['product', 'key']

class EditLog(models.Model):
    ACTION_CHOICES = [
        ('created', 'Created'),
        ('updated', 'Updated'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='edit_logs')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    details = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.product.name} - {self.get_action_display()} by {self.user.username}"
    
    class Meta:
        ordering = ['-timestamp']
