from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomLoginForm, ProfileUpdateForm
from core.models import Cart


def register_view(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('core:home')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Transfer session cart to user
            session_key = request.session.session_key
            if session_key:
                try:
                    session_cart = Cart.objects.get(session_key=session_key)
                    user_cart, created = Cart.objects.get_or_create(user=user)
                    # Transfer items
                    for item in session_cart.items.all():
                        item.cart = user_cart
                        item.save()
                    session_cart.delete()
                except Cart.DoesNotExist:
                    pass
            
            login(request, user)
            messages.success(request, 'Welcome to Bake with Love! Your account has been created.')
            return redirect('dashboard:index')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('core:home')
    
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            
            # Transfer session cart to user
            session_key = request.session.session_key
            if session_key:
                try:
                    session_cart = Cart.objects.get(session_key=session_key)
                    user_cart, created = Cart.objects.get_or_create(user=user)
                    # Transfer items
                    for item in session_cart.items.all():
                        item.cart = user_cart
                        item.save()
                    session_cart.delete()
                except Cart.DoesNotExist:
                    pass
            
            login(request, user)
            messages.success(request, f'Welcome back, {user.full_name}!')
            
            # Redirect to next page or dashboard
            next_url = request.GET.get('next', 'dashboard:index')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid email or password.')
    else:
        form = CustomLoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """User logout view"""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('core:home')


@login_required
def profile_view(request):
    """User profile view"""
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    
    return render(request, 'accounts/profile.html', {'form': form})
