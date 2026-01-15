"""
Order Spam Protection Module

This module provides anti-spam functionality for the ordering system:
- Max 2 orders per day per phone number
- Blocking users with repeated cancellations (3+)
- IP-based cooldown between orders (5 minutes)
"""

from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


class BlockedUser(models.Model):
    """Model to store permanently blocked users/phones/IPs"""
    REASON_CHOICES = [
        ('cancelled', 'Too many cancelled orders'),
        ('spam', 'Spam behavior'),
        ('manual', 'Manually blocked by admin'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='blocks'
    )
    phone = models.CharField(max_length=20, blank=True, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True, db_index=True)
    reason = models.CharField(max_length=20, choices=REASON_CHOICES, default='manual')
    notes = models.TextField(blank=True)
    blocked_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Blocked User'
        verbose_name_plural = 'Blocked Users'
    
    def __str__(self):
        if self.user:
            return f"Blocked: {self.user.email}"
        elif self.phone:
            return f"Blocked Phone: {self.phone}"
        return f"Blocked IP: {self.ip_address}"


class OrderRateLimit(models.Model):
    """Model to track order rate limits per phone/IP"""
    phone = models.CharField(max_length=20, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True, db_index=True)
    date = models.DateField(db_index=True)
    order_count = models.PositiveIntegerField(default=0)
    last_order_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['phone', 'date']
        verbose_name = 'Order Rate Limit'
        verbose_name_plural = 'Order Rate Limits'
    
    def __str__(self):
        return f"{self.phone} - {self.date}: {self.order_count} orders"


# ============== Validation Functions ==============

def get_client_ip(request):
    """Extract client IP from request, handling proxies"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def check_phone_daily_limit(phone, max_orders=2):
    """
    Check if phone number has exceeded daily order limit.
    Returns (is_allowed, message)
    """
    today = timezone.now().date()
    
    try:
        rate_limit = OrderRateLimit.objects.get(phone=phone, date=today)
        if rate_limit.order_count >= max_orders:
            return False, f"Maximum {max_orders} orders per day allowed. Please try again tomorrow."
    except OrderRateLimit.DoesNotExist:
        pass
    
    return True, None


def check_user_not_blocked(user=None, phone=None, ip_address=None):
    """
    Check if user, phone, or IP is blocked.
    Returns (is_allowed, message)
    """
    blocks = BlockedUser.objects.filter(is_active=True)
    
    if user:
        if blocks.filter(user=user).exists():
            return False, "Your account has been blocked due to policy violations."
    
    if phone:
        if blocks.filter(phone=phone).exists():
            return False, "This phone number has been blocked due to policy violations."
    
    if ip_address:
        if blocks.filter(ip_address=ip_address).exists():
            return False, "Access denied. Please contact support."
    
    return True, None


def check_ip_cooldown(ip_address, cooldown_minutes=5):
    """
    Check if IP has waited long enough since last order.
    Returns (is_allowed, message)
    """
    if not ip_address:
        return True, None
    
    cooldown_threshold = timezone.now() - timedelta(minutes=cooldown_minutes)
    
    recent_order = OrderRateLimit.objects.filter(
        ip_address=ip_address,
        last_order_at__gte=cooldown_threshold
    ).first()
    
    if recent_order:
        wait_time = (recent_order.last_order_at + timedelta(minutes=cooldown_minutes) - timezone.now())
        minutes_left = max(1, int(wait_time.total_seconds() / 60))
        return False, f"Please wait {minutes_left} minute(s) before placing another order."
    
    return True, None


def record_order(phone, ip_address):
    """Record a new order for rate limiting purposes"""
    today = timezone.now().date()
    
    rate_limit, created = OrderRateLimit.objects.get_or_create(
        phone=phone,
        date=today,
        defaults={'ip_address': ip_address, 'order_count': 0}
    )
    
    rate_limit.order_count += 1
    rate_limit.ip_address = ip_address
    rate_limit.save()


def check_cancellation_threshold(user, threshold=3):
    """
    Check if user has too many cancelled orders and block if needed.
    Returns number of cancelled orders.
    """
    from .models import Order
    
    cancelled_count = Order.objects.filter(
        user=user,
        status='cancelled'
    ).count()
    
    if cancelled_count >= threshold:
        # Block the user if not already blocked
        BlockedUser.objects.get_or_create(
            user=user,
            reason='cancelled',
            defaults={
                'phone': user.phone if hasattr(user, 'phone') else '',
                'notes': f'Auto-blocked after {cancelled_count} cancelled orders'
            }
        )
    
    return cancelled_count


def validate_order_allowed(request, phone):
    """
    Main validation function - checks all spam rules.
    Returns (is_allowed, error_message)
    """
    user = request.user if request.user.is_authenticated else None
    ip_address = get_client_ip(request)
    
    # Check if user/phone/IP is blocked
    allowed, message = check_user_not_blocked(user, phone, ip_address)
    if not allowed:
        return False, message
    
    # Check phone daily limit
    allowed, message = check_phone_daily_limit(phone)
    if not allowed:
        return False, message
    
    # Check IP cooldown
    allowed, message = check_ip_cooldown(ip_address)
    if not allowed:
        return False, message
    
    return True, None
