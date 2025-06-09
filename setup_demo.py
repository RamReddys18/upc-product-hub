
#!/usr/bin/env python
"""
Setup script to create demo users and sample data for the UPC System
Run this after migrations: python setup_demo.py
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'upc_system.settings')
django.setup()

from django.contrib.auth import get_user_model
from products.models import Category, Size, Product, ProductAttribute, EditLog
from notifications.models import Notification

User = get_user_model()

def create_demo_users():
    """Create demo users for testing"""
    print("Creating demo users...")
    
    # Create admin user
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@example.com',
            'first_name': 'System',
            'last_name': 'Administrator',
            'role': 'admin',
            'is_superuser': True,
            'is_staff': True,
        }
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        print("✓ Admin user created (username: admin, password: admin123)")
    
    # Create manager user
    manager_user, created = User.objects.get_or_create(
        username='manager',
        defaults={
            'email': 'manager@example.com',
            'first_name': 'Product',
            'last_name': 'Manager',
            'role': 'manager',
        }
    )
    if created:
        manager_user.set_password('manager123')
        manager_user.save()
        print("✓ Manager user created (username: manager, password: manager123)")
    
    # Create team member user
    team_user, created = User.objects.get_or_create(
        username='team',
        defaults={
            'email': 'team@example.com',
            'first_name': 'Team',
            'last_name': 'Member',
            'role': 'team_member',
        }
    )
    if created:
        team_user.set_password('team123')
        team_user.save()
        print("✓ Team member user created (username: team, password: team123)")
    
    return admin_user, manager_user, team_user

def create_sample_data():
    """Create sample categories, sizes, and products"""
    print("Creating sample data...")
    
    # Create categories
    categories = ['Electronics', 'Food & Beverages', 'Clothing', 'Home & Garden', 'Health & Beauty']
    for cat_name in categories:
        Category.objects.get_or_create(name=cat_name)
    print("✓ Categories created")
    
    # Create sizes
    sizes = ['Small', 'Medium', 'Large', 'Extra Large', '12 oz', '16 oz', '24 oz', 'One Size']
    for size_name in sizes:
        Size.objects.get_or_create(name=size_name)
    print("✓ Sizes created")
    
    # Get users
    team_user = User.objects.get(username='team')
    manager_user = User.objects.get(username='manager')
    
    # Create sample products
    sample_products = [
        {
            'name': 'Organic Coffee Beans',
            'upc': '123456789012',
            'ean': '1234567890123',
            'brand_name': 'Green Mountain',
            'description': 'Premium organic coffee beans, medium roast',
            'category': 'Food & Beverages',
            'size': '12 oz',
            'status': 'approved',
            'attributes': {'Country of Origin': 'Colombia', 'Organic': 'Yes'}
        },
        {
            'name': 'Wireless Bluetooth Headphones',
            'upc': '234567890123',
            'ean': '2345678901234',
            'brand_name': 'TechSound',
            'description': 'High-quality wireless headphones with noise cancellation',
            'category': 'Electronics',
            'size': 'One Size',
            'status': 'under_review',
            'attributes': {'Battery Life': '30 hours', 'Warranty': '2 years'}
        },
        {
            'name': 'Cotton T-Shirt',
            'upc': '345678901234',
            'ean': '3456789012345',
            'brand_name': 'Comfort Wear',
            'description': 'Soft cotton t-shirt, comfortable fit',
            'category': 'Clothing',
            'size': 'Medium',
            'status': 'rejected',
            'attributes': {'Material': '100% Cotton', 'Care': 'Machine Wash'}
        },
    ]
    
    for product_data in sample_products:
        # Get category and size objects
        category = Category.objects.get(name=product_data['category'])
        size = Size.objects.get(name=product_data['size'])
        attributes = product_data.pop('attributes')
        
        product, created = Product.objects.get_or_create(
            upc=product_data['upc'],
            defaults={
                **product_data,
                'category': category,
                'size': size,
                'submitted_by': team_user,
                'reviewed_by': manager_user if product_data['status'] != 'under_review' else None,
            }
        )
        
        if created:
            # Add attributes
            for key, value in attributes.items():
                ProductAttribute.objects.create(
                    product=product,
                    key=key,
                    value=value
                )
            
            # Create edit log
            EditLog.objects.create(
                product=product,
                user=team_user,
                action='created',
                details=f"Product created: {product.name}"
            )
            
            # If rejected, create a notification
            if product.status == 'rejected':
                product.rejection_reason = "Please provide more detailed description and verify UPC code."
                product.save()
                
                Notification.objects.create(
                    user=team_user,
                    title=f"Product Rejected: {product.name}",
                    message=f"Your product '{product.name}' has been rejected. Reason: {product.rejection_reason}",
                    link=f"/dashboard/products/{product.pk}/edit/"
                )
                
                EditLog.objects.create(
                    product=product,
                    user=manager_user,
                    action='rejected',
                    details=product.rejection_reason
                )
    
    print("✓ Sample products created")

def main():
    """Main setup function"""
    print("Setting up UPC System demo data...")
    print("=" * 50)
    
    create_demo_users()
    create_sample_data()
    
    print("=" * 50)
    print("Demo setup complete!")
    print("\nYou can now login with:")
    print("Admin: username=admin, password=admin123")
    print("Manager: username=manager, password=manager123")
    print("Team Member: username=team, password=team123")
    print("\nRun the server with: python manage.py runserver")

if __name__ == '__main__':
    main()
