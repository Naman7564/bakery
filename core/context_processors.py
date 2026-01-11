from .models import Cart


def cart_count(request):
    """Context processor to add cart count to all templates"""
    count = 0
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            count = cart.item_count
        except Cart.DoesNotExist:
            pass
    else:
        session_key = request.session.session_key
        if session_key:
            try:
                cart = Cart.objects.get(session_key=session_key)
                count = cart.item_count
            except Cart.DoesNotExist:
                pass
    return {'cart_count': count}
