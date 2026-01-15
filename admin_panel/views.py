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
            old_status = order.status
            order.status = new_status
            order.save()
            messages.success(request, f'Order status updated to {order.get_status_display()}')
            
            # Check cancellation threshold if order was cancelled
            if new_status == 'cancelled' and old_status != 'cancelled':
                from core.spam_protection import check_cancellation_threshold
                cancelled_count = check_cancellation_threshold(order.user)
                if cancelled_count >= 3:
                    messages.warning(
                        request, 
                        f'User {order.user.email} has been auto-blocked after {cancelled_count} cancellations.'
                    )
    
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


# Blocked Users Management (Spam Protection)
@admin_required
def blocked_users_list(request):
    """List all blocked users/phones/IPs"""
    from core.spam_protection import BlockedUser, OrderRateLimit
    
    blocked_users = BlockedUser.objects.all().order_by('-blocked_at')
    
    # Filter by status
    status = request.GET.get('status')
    if status == 'active':
        blocked_users = blocked_users.filter(is_active=True)
    elif status == 'inactive':
        blocked_users = blocked_users.filter(is_active=False)
    
    # Filter by reason
    reason = request.GET.get('reason')
    if reason:
        blocked_users = blocked_users.filter(reason=reason)
    
    # Search
    search = request.GET.get('q')
    if search:
        from django.db.models import Q
        blocked_users = blocked_users.filter(
            Q(phone__icontains=search) |
            Q(ip_address__icontains=search) |
            Q(user__email__icontains=search)
        )
    
    # Get today's rate limits for stats
    today_limits = OrderRateLimit.objects.filter(date=timezone.now().date())
    
    context = {
        'blocked_users': blocked_users,
        'current_status': status,
        'current_reason': reason,
        'search_query': search,
        'total_blocked': BlockedUser.objects.filter(is_active=True).count(),
        'today_orders_tracked': today_limits.count(),
    }
    return render(request, 'admin_panel/blocked_users.html', context)


@admin_required
def blocked_user_create(request):
    """Manually block a user/phone/IP"""
    from core.spam_protection import BlockedUser
    
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        phone = request.POST.get('phone', '').strip()
        ip_address = request.POST.get('ip_address', '').strip()
        reason = request.POST.get('reason', 'manual')
        notes = request.POST.get('notes', '')
        
        user = None
        if user_id:
            user = CustomUser.objects.filter(id=user_id).first()
        
        BlockedUser.objects.create(
            user=user,
            phone=phone,
            ip_address=ip_address if ip_address else None,
            reason=reason,
            notes=notes
        )
        messages.success(request, 'Block entry created successfully!')
        return redirect('admin_panel:blocked_users')
    
    users = CustomUser.objects.filter(is_admin_user=False, is_superuser=False)
    context = {
        'users': users,
        'reasons': BlockedUser.REASON_CHOICES,
    }
    return render(request, 'admin_panel/blocked_user_form.html', context)


@admin_required
def blocked_user_edit(request, block_id):
    """Edit a block entry"""
    from core.spam_protection import BlockedUser
    
    block = get_object_or_404(BlockedUser, id=block_id)
    
    if request.method == 'POST':
        block.phone = request.POST.get('phone', '').strip()
        ip_address = request.POST.get('ip_address', '').strip()
        block.ip_address = ip_address if ip_address else None
        block.reason = request.POST.get('reason', 'manual')
        block.notes = request.POST.get('notes', '')
        block.is_active = request.POST.get('is_active') == 'on'
        block.save()
        messages.success(request, 'Block entry updated successfully!')
        return redirect('admin_panel:blocked_users')
    
    users = CustomUser.objects.filter(is_admin_user=False, is_superuser=False)
    context = {
        'block': block,
        'users': users,
        'reasons': BlockedUser.REASON_CHOICES,
    }
    return render(request, 'admin_panel/blocked_user_form.html', context)


@admin_required
def blocked_user_delete(request, block_id):
    """Delete a block entry"""
    from core.spam_protection import BlockedUser
    
    block = get_object_or_404(BlockedUser, id=block_id)
    if request.method == 'POST':
        block.delete()
        messages.success(request, 'Block entry deleted successfully!')
    return redirect('admin_panel:blocked_users')


@admin_required
def blocked_user_toggle(request, block_id):
    """Toggle block active status"""
    from core.spam_protection import BlockedUser
    
    block = get_object_or_404(BlockedUser, id=block_id)
    block.is_active = not block.is_active
    block.save()
    
    status = 'activated' if block.is_active else 'deactivated'
    messages.success(request, f'Block {status} successfully!')
    return redirect('admin_panel:blocked_users')

