
import csv
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db.models import Q, Count
from django.utils import timezone
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model
from .models import Product, Category, Size, EditLog, ProductAttribute
from .forms import ProductForm, ProductAttributeFormSet, ReviewForm, CategoryForm, SizeForm
from notifications.models import Notification

User = get_user_model()

def is_admin(user):
    return user.is_authenticated and user.is_admin()

def is_manager_or_admin(user):
    return user.is_authenticated and user.can_review_products()

@login_required
def dashboard_redirect(request):
    """Redirect users to their appropriate dashboard"""
    if request.user.is_admin():
        return redirect('products:admin_dashboard')
    elif request.user.is_manager():
        return redirect('products:manager_dashboard')
    else:
        return redirect('products:team_dashboard')

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """Admin dashboard with comprehensive statistics"""
    # Get statistics
    total_products = Product.objects.count()
    approved_products = Product.objects.filter(status='approved').count()
    under_review_products = Product.objects.filter(status='under_review').count()
    rejected_products = Product.objects.filter(status='rejected').count()
    
    # Recent activities
    recent_products = Product.objects.select_related('submitted_by', 'category', 'size')[:10]
    recent_logs = EditLog.objects.select_related('user', 'product')[:10]
    
    # User statistics
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    
    context = {
        'total_products': total_products,
        'approved_products': approved_products,
        'under_review_products': under_review_products,
        'rejected_products': rejected_products,
        'recent_products': recent_products,
        'recent_logs': recent_logs,
        'total_users': total_users,
        'active_users': active_users,
    }
    return render(request, 'products/admin_dashboard.html', context)

@login_required
@user_passes_test(is_manager_or_admin)
def manager_dashboard(request):
    """Manager dashboard focused on review tasks"""
    # Products needing review
    under_review_products = Product.objects.filter(status='under_review').select_related('submitted_by', 'category', 'size')
    
    # Statistics
    total_reviewed = Product.objects.filter(reviewed_by=request.user).count()
    approved_by_me = Product.objects.filter(reviewed_by=request.user, status='approved').count()
    rejected_by_me = Product.objects.filter(reviewed_by=request.user, status='rejected').count()
    
    # Recent activities
    recent_logs = EditLog.objects.filter(user=request.user).select_related('product')[:10]
    
    context = {
        'under_review_products': under_review_products,
        'total_reviewed': total_reviewed,
        'approved_by_me': approved_by_me,
        'rejected_by_me': rejected_by_me,
        'recent_logs': recent_logs,
    }
    return render(request, 'products/manager_dashboard.html', context)

@login_required
def team_dashboard(request):
    """Team member dashboard showing their submissions"""
    # User's products
    my_products = Product.objects.filter(submitted_by=request.user).select_related('category', 'size')
    
    # Statistics
    total_submitted = my_products.count()
    approved_count = my_products.filter(status='approved').count()
    under_review_count = my_products.filter(status='under_review').count()
    rejected_count = my_products.filter(status='rejected').count()
    
    # Recent submissions
    recent_products = my_products[:10]
    
    context = {
        'my_products': my_products,
        'total_submitted': total_submitted,
        'approved_count': approved_count,
        'under_review_count': under_review_count,
        'rejected_count': rejected_count,
        'recent_products': recent_products,
    }
    return render(request, 'products/team_dashboard.html', context)

@login_required
def product_list(request):
    """List all products with filtering and search"""
    products = Product.objects.select_related('submitted_by', 'category', 'size', 'reviewed_by')
    
    # Apply filters based on user role
    if request.user.is_team_member():
        products = products.filter(submitted_by=request.user)
    
    # Search functionality
    search = request.GET.get('search')
    if search:
        products = products.filter(
            Q(name__icontains=search) |
            Q(upc__icontains=search) |
            Q(brand_name__icontains=search)
        )
    
    # Status filter
    status = request.GET.get('status')
    if status:
        products = products.filter(status=status)
    
    # User filter (admin only)
    user_filter = request.GET.get('user')
    if user_filter and request.user.is_admin():
        products = products.filter(submitted_by_id=user_filter)
    
    # Pagination
    paginator = Paginator(products, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get users for filter dropdown (admin only)
    users = User.objects.all() if request.user.is_admin() else None
    
    context = {
        'page_obj': page_obj,
        'search': search,
        'status': status,
        'user_filter': user_filter,
        'users': users,
    }
    return render(request, 'products/product_list.html', context)

@login_required
def product_detail(request, pk):
    """View product details"""
    product = get_object_or_404(Product, pk=pk)
    
    # Check permissions
    if request.user.is_team_member() and product.submitted_by != request.user:
        messages.error(request, "You don't have permission to view this product.")
        return redirect('products:product_list')
    
    # Get product attributes and edit logs
    attributes = product.attributes.all()
    edit_logs = product.edit_logs.select_related('user').all()
    
    context = {
        'product': product,
        'attributes': attributes,
        'edit_logs': edit_logs,
    }
    return render(request, 'products/product_detail.html', context)

@login_required
def product_create(request):
    """Create a new product"""
    if request.method == 'POST':
        form = ProductForm(request.POST)
        formset = ProductAttributeFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid():
            product = form.save(commit=False)
            product.submitted_by = request.user
            product.save()
            
            # Save attributes
            formset.instance = product
            formset.save()
            
            # Create edit log
            EditLog.objects.create(
                product=product,
                user=request.user,
                action='created',
                details=f"Product created: {product.name}"
            )
            
            messages.success(request, 'Product submitted successfully and is now under review.')
            return redirect('products:product_detail', pk=product.pk)
    else:
        form = ProductForm()
        formset = ProductAttributeFormSet()
    
    context = {
        'form': form,
        'formset': formset,
        'title': 'Create Product',
    }
    return render(request, 'products/product_form.html', context)

@login_required
def product_edit(request, pk):
    """Edit a product (only allowed for rejected products by their submitter)"""
    product = get_object_or_404(Product, pk=pk)
    
    # Check permissions
    if not product.can_edit(request.user):
        messages.error(request, "You can only edit your own rejected products.")
        return redirect('products:product_detail', pk=product.pk)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        formset = ProductAttributeFormSet(request.POST, instance=product)
        
        if form.is_valid() and formset.is_valid():
            product = form.save(commit=False)
            product.status = 'under_review'  # Reset status to under review
            product.rejection_reason = None  # Clear rejection reason
            product.save()
            
            formset.save()
            
            # Create edit log
            EditLog.objects.create(
                product=product,
                user=request.user,
                action='updated',
                details=f"Product updated and resubmitted for review"
            )
            
            messages.success(request, 'Product updated and resubmitted for review.')
            return redirect('products:product_detail', pk=product.pk)
    else:
        form = ProductForm(instance=product)
        formset = ProductAttributeFormSet(instance=product)
    
    context = {
        'form': form,
        'formset': formset,
        'product': product,
        'title': 'Edit Product',
    }
    return render(request, 'products/product_form.html', context)

@login_required
@user_passes_test(is_manager_or_admin)
def product_review(request, pk):
    """Review a product (approve or reject)"""
    product = get_object_or_404(Product, pk=pk)
    
    if product.status != 'under_review':
        messages.error(request, "This product is not under review.")
        return redirect('products:product_detail', pk=product.pk)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            action = form.cleaned_data['action']
            rejection_reason = form.cleaned_data.get('rejection_reason')
            
            # Update product status
            product.status = 'approved' if action == 'approve' else 'rejected'
            product.reviewed_by = request.user
            product.reviewed_at = timezone.now()
            
            if action == 'reject':
                product.rejection_reason = rejection_reason
            
            product.save()
            
            # Create edit log
            EditLog.objects.create(
                product=product,
                user=request.user,
                action=action,
                details=rejection_reason if action == 'reject' else f"Product approved by {request.user.username}"
            )
            
            # Create notification for product submitter
            if action == 'reject':
                Notification.objects.create(
                    user=product.submitted_by,
                    title=f"Product Rejected: {product.name}",
                    message=f"Your product '{product.name}' has been rejected. Reason: {rejection_reason}",
                    link=f"/dashboard/products/{product.pk}/edit/"
                )
            
            messages.success(request, f'Product {action}d successfully.')
            return redirect('products:product_detail', pk=product.pk)
    else:
        form = ReviewForm()
    
    context = {
        'form': form,
        'product': product,
    }
    return render(request, 'products/product_review.html', context)

@login_required
@user_passes_test(is_admin)
def manage_categories(request):
    """Manage product categories"""
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category added successfully.')
            return redirect('products:manage_categories')
    else:
        form = CategoryForm()
    
    categories = Category.objects.all().order_by('name')
    
    context = {
        'form': form,
        'categories': categories,
    }
    return render(request, 'products/manage_categories.html', context)

@login_required
@user_passes_test(is_admin)
def manage_sizes(request):
    """Manage product sizes"""
    if request.method == 'POST':
        form = SizeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Size added successfully.')
            return redirect('products:manage_sizes')
    else:
        form = SizeForm()
    
    sizes = Size.objects.all().order_by('name')
    
    context = {
        'form': form,
        'sizes': sizes,
    }
    return render(request, 'products/manage_sizes.html', context)

@login_required
@user_passes_test(is_admin)
def manage_users(request):
    """Manage users"""
    users = User.objects.all().order_by('username')
    
    # Search functionality
    search = request.GET.get('search')
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search': search,
    }
    return render(request, 'products/manage_users.html', context)

@login_required
@user_passes_test(is_admin)
def toggle_user_status(request, user_id):
    """Toggle user active status via AJAX"""
    if request.method == 'POST':
        user = get_object_or_404(User, pk=user_id)
        user.is_active = not user.is_active
        user.save()
        return JsonResponse({'success': True, 'is_active': user.is_active})
    return JsonResponse({'success': False})

@login_required
@user_passes_test(is_admin)
def edit_logs(request):
    """View all edit logs"""
    logs = EditLog.objects.select_related('user', 'product').all()
    
    # Search functionality
    search = request.GET.get('search')
    if search:
        logs = logs.filter(
            Q(product__name__icontains=search) |
            Q(user__username__icontains=search) |
            Q(details__icontains=search)
        )
    
    # Action filter
    action = request.GET.get('action')
    if action:
        logs = logs.filter(action=action)
    
    # Pagination
    paginator = Paginator(logs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search': search,
        'action': action,
        'action_choices': EditLog.ACTION_CHOICES,
    }
    return render(request, 'products/edit_logs.html', context)

@login_required
@user_passes_test(is_admin)
def export_products(request):
    """Export products to CSV"""
    # Get filtered products based on query parameters
    products = Product.objects.select_related('submitted_by', 'category', 'size', 'reviewed_by')
    
    # Apply filters
    status = request.GET.get('status')
    if status:
        products = products.filter(status=status)
    
    user_filter = request.GET.get('user')
    if user_filter:
        products = products.filter(submitted_by_id=user_filter)
    
    search = request.GET.get('search')
    if search:
        products = products.filter(
            Q(name__icontains=search) |
            Q(upc__icontains=search) |
            Q(brand_name__icontains=search)
        )
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="products_export.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Name', 'UPC', 'EAN', 'Brand Name', 'Description', 'Size', 'Category',
        'Status', 'Submitted By', 'Reviewed By', 'Created At', 'Updated At'
    ])
    
    for product in products:
        writer.writerow([
            product.name,
            product.upc,
            product.ean or '',
            product.brand_name,
            product.description,
            product.size.name,
            product.category.name,
            product.get_status_display(),
            product.submitted_by.username,
            product.reviewed_by.username if product.reviewed_by else '',
            product.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            product.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
        ])
    
    return response
