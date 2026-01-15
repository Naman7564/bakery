from django.contrib import admin
from .models import Category, Product, Cart, CartItem, Order, OrderItem, ContactMessage


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ['is_active']
    search_fields = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'stock', 'is_featured', 'is_available']
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ['category', 'is_featured', 'is_special', 'is_available']
    search_fields = ['name', 'description']
    list_editable = ['is_featured', 'is_available', 'stock']


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'session_key', 'created_at']
    inlines = [CartItemInline]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'product_name', 'price', 'quantity']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'total', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order_number', 'user__email']
    inlines = [OrderItemInline]
    readonly_fields = ['order_number', 'total']


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['name', 'email', 'subject']


# Spam Protection Models
from .spam_protection import BlockedUser, OrderRateLimit


@admin.register(BlockedUser)
class BlockedUserAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'reason', 'is_active', 'blocked_at']
    list_filter = ['reason', 'is_active', 'blocked_at']
    search_fields = ['user__email', 'phone', 'ip_address']
    list_editable = ['is_active']
    readonly_fields = ['blocked_at']
    
    fieldsets = (
        (None, {
            'fields': ('user', 'phone', 'ip_address')
        }),
        ('Block Details', {
            'fields': ('reason', 'notes', 'is_active', 'blocked_at')
        }),
    )


@admin.register(OrderRateLimit)
class OrderRateLimitAdmin(admin.ModelAdmin):
    list_display = ['phone', 'ip_address', 'date', 'order_count', 'last_order_at']
    list_filter = ['date']
    search_fields = ['phone', 'ip_address']
    readonly_fields = ['phone', 'ip_address', 'date', 'order_count', 'last_order_at']
    date_hierarchy = 'date'

