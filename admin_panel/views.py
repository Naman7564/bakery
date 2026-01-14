from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta

from .decorators import admin_required
from .forms import ProductForm, CategoryForm, AdminUserPasswordChangeForm
from core.models import Product, Category, Order, ContactMessage
from accounts.models import CustomUser


def admin_login(request):
    """Admin login view"""
    if request.user.is_authenticated:
        if request.user.is_admin_user or request.user.is_superuser:
            return redirect('admin_panel:dashboard')
        return redirect('core:home')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            if user.is_admin_user or user.is_superuser:
                login(request, user)
                messages.success(request, f'Welcome back, {user.full_name}!')
                return redirect('admin_panel:dashboard')
            else:
                messages.error(request, 'You do not have admin privileges.')
        else:
            messages.error(request, 'Invalid email or password.')
    
    return render(request, 'admin_panel/login.html')


def admin_logout(request):
    """Admin logout view"""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('admin_panel:login')


@admin_required
def dashboard(request):
    """Admin dashboard with analytics"""
    # Get date range
    today = timezone.now()
    last_30_days = today - timedelta(days=30)
    
    # Statistics
    total_revenue = Order.objects.filter(
        status='delivered'
    ).aggregate(Sum('total'))['total__sum'] or 0
    
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='pending').count()
    total_products = Product.objects.count()
    total_users = CustomUser.objects.filter(is_admin_user=False, is_superuser=False).count()
    
    # Recent data
    recent_orders = Order.objects.all()[:10]
    new_messages = ContactMessage.objects.filter(is_read=False).count()
    
    # Orders by status
    orders_by_status = Order.objects.values('status').annotate(count=Count('id'))
    
    context = {
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'total_products': total_products,
        'total_users': total_users,
        'recent_orders': recent_orders,
        'new_messages': new_messages,
        'orders_by_status': orders_by_status,
    }
    return render(request, 'admin_panel/dashboard.html', context)


# Product Management
@admin_required
def products_list(request):
    """List all products"""
    products = Product.objects.all()
    categories = Category.objects.all()
    
    # Filter by category
    category = request.GET.get('category')
    if category:
        products = products.filter(category__slug=category)
    
    # Search
    search = request.GET.get('q')
    if search:
        products = products.filter(name__icontains=search)
    
    context = {
        'products': products,
        'categories': categories,
        'current_category': category,
        'search_query': search,
    }
    return render(request, 'admin_panel/products.html', context)


@admin_required
def product_create(request):
    """Create a new product"""
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product created successfully!')
            return redirect('admin_panel:products')
    else:
        form = ProductForm()
    
    return render(request, 'admin_panel/product_form.html', {'form': form, 'title': 'Add Product'})


@admin_required
def product_edit(request, product_id):
    """Edit an existing product"""
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('admin_panel:products')
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'admin_panel/product_form.html', {'form': form, 'title': 'Edit Product', 'product': product})


@admin_required
def product_delete(request, product_id):
    """Delete a product"""
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully!')
    return redirect('admin_panel:products')


# Category Management
@admin_required
def categories_list(request):
    """List all categories"""
    categories = Category.objects.annotate(product_count=Count('products'))
    return render(request, 'admin_panel/categories.html', {'categories': categories})


@admin_required
def category_create(request):
    """Create a new category"""
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category created successfully!')
            return redirect('admin_panel:categories')
    else:
        form = CategoryForm()
    
    return render(request, 'admin_panel/category_form.html', {'form': form, 'title': 'Add Category'})


@admin_required
def category_edit(request, category_id):
    """Edit an existing category"""
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully!')
            return redirect('admin_panel:categories')
    else:
        form = CategoryForm(instance=category)
    
    return render(request, 'admin_panel/category_form.html', {'form': form, 'title': 'Edit Category', 'category': category})


@admin_required
def category_delete(request, category_id):
    """Delete a category"""
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully!')
    return redirect('admin_panel:categories')


# Order Management
@admin_required
def orders_list(request):
    """List all orders"""
    orders = Order.objects.all()
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        orders = orders.filter(status=status)
    
    context = {'orders': orders, 'current_status': status}
    return render(request, 'admin_panel/orders.html', context)


@admin_required
def order_detail(request, order_id):
    """View order details"""
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status:
            order.status = new_status
            order.save()
            messages.success(request, f'Order status updated to {order.get_status_display()}')
    
    return render(request, 'admin_panel/order_detail.html', {'order': order})


# User Management
@admin_required
def users_list(request):
    """List all users"""
    users = CustomUser.objects.filter(is_admin_user=False, is_superuser=False)
    
    # Search
    search = request.GET.get('q')
    if search:
        users = users.filter(email__icontains=search) | users.filter(username__icontains=search)
    
    context = {'users': users, 'search_query': search}
    return render(request, 'admin_panel/users.html', context)


@admin_required
def user_detail(request, user_id):
    """View user details"""
    user = get_object_or_404(CustomUser, id=user_id)
    orders = Order.objects.filter(user=user)
    context = {'user_obj': user, 'orders': orders}
    return render(request, 'admin_panel/user_detail.html', context)


# Messages
@admin_required
def messages_list(request):
    """List all contact messages"""
    contact_messages = ContactMessage.objects.all()
    unread = request.GET.get('unread')
    if unread:
        contact_messages = contact_messages.filter(is_read=False)
    
    return render(request, 'admin_panel/messages.html', {'contact_messages': contact_messages})


@admin_required
def message_detail(request, message_id):
    """View message details"""
    message = get_object_or_404(ContactMessage, id=message_id)
    if not message.is_read:
        message.is_read = True
        message.save()
    return render(request, 'admin_panel/message_detail.html', {'message': message})


# User Password Change
@admin_required
def user_change_password(request, user_id):
    """Change a user's password"""
    user = get_object_or_404(CustomUser, id=user_id)
    
    if request.method == 'POST':
        form = AdminUserPasswordChangeForm(request.POST)
        if form.is_valid():
            user.set_password(form.cleaned_data['new_password1'])
            user.save()
            messages.success(request, f'Password changed successfully for {user.email}!')
            return redirect('admin_panel:user_detail', user_id=user_id)
    else:
        form = AdminUserPasswordChangeForm()
    
    context = {
        'form': form,
        'user_obj': user,
    }
    return render(request, 'admin_panel/user_change_password.html', context)
