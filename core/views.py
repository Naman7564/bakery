from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q
import uuid

from .models import Category, Product, Cart, CartItem, Order, OrderItem, ContactMessage


def get_or_create_cart(request):
    """Get or create a cart for the current user/session"""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_key=session_key)
    return cart


def home(request):
    """Homepage view"""
    categories = Category.objects.filter(is_active=True)[:6]
    featured_products = Product.objects.filter(is_featured=True, is_available=True)[:6]
    special_products = Product.objects.filter(is_special=True, is_available=True)[:6]
    
    context = {
        'categories': categories,
        'featured_products': featured_products,
        'special_products': special_products,
    }
    return render(request, 'home.html', context)


def products(request):
    """Product listing view"""
    products = Product.objects.filter(is_available=True)
    categories = Category.objects.filter(is_active=True)

    # Filter by category
    category_slug = request.GET.get('category')
    current_category = None
    if category_slug:
        current_category = get_object_or_404(Category, slug=category_slug, is_active=True)
        products = products.filter(category=current_category)

    # Search
    search_query = request.GET.get('q')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | Q(description__icontains=search_query)
        )

    context = {
        'products': products,
        'categories': categories,
        'current_category': current_category,  # pass the object, not just the slug
        'search_query': search_query,
    }
    return render(request, 'core/products.html', context)


def product_detail(request, slug):
    """Product detail view"""
    product = get_object_or_404(Product, slug=slug, is_available=True)
    related_products = Product.objects.filter(
        category=product.category, is_available=True
    ).exclude(id=product.id)[:4]
    
    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'core/product_detail.html', context)


def category_detail(request, slug):
    """Category detail view"""
    category = get_object_or_404(Category, slug=slug, is_active=True)
    products = category.products.filter(is_available=True)
    
    context = {
        'category': category,
        'products': products,
    }
    return render(request, 'core/category_detail.html', context)


def about(request):
    """About page"""
    return render(request, 'core/about.html')


def contact(request):
    """Contact page"""
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        ContactMessage.objects.create(
            name=name,
            email=email,
            subject=subject,
            message=message
        )
        messages.success(request, 'Thank you for your message! We will get back to you soon.')
        return redirect('core:contact')
    
    return render(request, 'core/contact.html')


def cart_view(request):
    """Shopping cart view"""
    cart = get_or_create_cart(request)
    context = {'cart': cart}
    return render(request, 'core/cart.html', context)


@require_POST
def add_to_cart(request, product_id):
    """Add product to cart"""
    product = get_object_or_404(Product, id=product_id, is_available=True)
    cart = get_or_create_cart(request)
    
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 1}
    )
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_count': cart.item_count,
            'message': f'{product.name} added to cart!'
        })
    
    messages.success(request, f'{product.name} added to cart!')
    return redirect('core:cart')


@require_POST
def update_cart(request, item_id):
    """Update cart item quantity"""
    cart_item = get_object_or_404(CartItem, id=item_id)
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity > 0:
        cart_item.quantity = quantity
        cart_item.save()
    else:
        cart_item.delete()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_total': float(cart_item.cart.total),
            'item_subtotal': float(cart_item.subtotal) if quantity > 0 else 0,
            'cart_count': cart_item.cart.item_count
        })
    
    return redirect('core:cart')


@require_POST
def remove_from_cart(request, item_id):
    """Remove item from cart"""
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart = cart_item.cart
    cart_item.delete()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_total': float(cart.total),
            'cart_count': cart.item_count
        })
    
    messages.success(request, 'Item removed from cart.')
    return redirect('core:cart')


@login_required
def checkout(request):
    """Checkout view"""
    cart = get_or_create_cart(request)
    
    if cart.item_count == 0:
        messages.warning(request, 'Your cart is empty!')
        return redirect('core:products')
    
    if request.method == 'POST':
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        notes = request.POST.get('notes', '')
        
        # Create order
        order_number = f"BWL{uuid.uuid4().hex[:8].upper()}"
        order = Order.objects.create(
            user=request.user,
            order_number=order_number,
            total=cart.total,
            address=address,
            phone=phone,
            notes=notes
        )
        
        # Create order items
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                product_name=item.product.name,
                price=item.product.price,
                quantity=item.quantity
            )
        
        # Clear cart
        cart.items.all().delete()
        
        messages.success(request, f'Order placed successfully! Order number: {order_number}')
        return redirect('dashboard:order_detail', order_id=order.id)
    
    context = {'cart': cart}
    return render(request, 'core/checkout.html', context)
