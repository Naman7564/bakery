from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from core.models import Order


@login_required
def index(request):
    """User dashboard home"""
    recent_orders = Order.objects.filter(user=request.user)[:5]
    total_orders = Order.objects.filter(user=request.user).count()
    pending_orders = Order.objects.filter(user=request.user, status='pending').count()
    delivered_orders = Order.objects.filter(user=request.user, status='delivered').count()
    
    # Calculate total spent from delivered orders
    total_spent = Order.objects.filter(
        user=request.user, 
        status='delivered'
    ).aggregate(total=Sum('total'))['total'] or 0
    
    context = {
        'recent_orders': recent_orders,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'delivered_orders': delivered_orders,
        'total_spent': total_spent,
    }
    return render(request, 'dashboard/index.html', context)


@login_required
def orders(request):
    """User orders list"""
    orders = Order.objects.filter(user=request.user)
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        orders = orders.filter(status=status)
    
    context = {'orders': orders, 'current_status': status}
    return render(request, 'dashboard/orders.html', context)


@login_required
def order_detail(request, order_id):
    """Order detail view"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    context = {'order': order}
    return render(request, 'dashboard/order_detail.html', context)
