
from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # Dashboard URLs
    path('', views.dashboard_redirect, name='dashboard_redirect'),
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('manager/', views.manager_dashboard, name='manager_dashboard'),
    path('team/', views.team_dashboard, name='team_dashboard'),
    
    # Product URLs
    path('products/', views.product_list, name='product_list'),
    path('products/create/', views.product_create, name='product_create'),
    path('products/<int:pk>/', views.product_detail, name='product_detail'),
    path('products/<int:pk>/edit/', views.product_edit, name='product_edit'),
    path('products/<int:pk>/review/', views.product_review, name='product_review'),
    
    # Admin management URLs
    path('manage/categories/', views.manage_categories, name='manage_categories'),
    path('manage/sizes/', views.manage_sizes, name='manage_sizes'),
    path('manage/users/', views.manage_users, name='manage_users'),
    path('logs/', views.edit_logs, name='edit_logs'),
    path('export/', views.export_products, name='export_products'),
    
    # AJAX URLs
    path('ajax/toggle-user-status/<int:user_id>/', views.toggle_user_status, name='toggle_user_status'),
]
