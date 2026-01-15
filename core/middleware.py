"""
Custom Middleware for the Bakery Application
"""


class IPTrackingMiddleware:
    """
    Middleware to attach client IP address to the request object.
    This makes it easy to access the IP from any view.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Get client IP, handling proxies (like nginx)
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # X-Forwarded-For can contain multiple IPs; take the first one
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        
        # Attach IP to request for easy access
        request.client_ip = ip
        
        response = self.get_response(request)
        return response
