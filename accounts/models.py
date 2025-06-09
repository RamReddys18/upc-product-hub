
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('team_member', 'Team Member'),
        ('manager', 'Manager'),
        ('admin', 'Admin'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='team_member')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    def is_admin(self):
        return self.role == 'admin'
    
    def is_manager(self):
        return self.role == 'manager'
    
    def is_team_member(self):
        return self.role == 'team_member'
    
    def can_review_products(self):
        return self.role in ['admin', 'manager']
