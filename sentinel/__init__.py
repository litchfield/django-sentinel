"""
Convenience methods to avoid having to use hasattr, which
covers cases where the middleware isn't loaded / didn't load

Obviously you can still use request.brownlisted in your templates
"""

def is_whitelisted(request):
    return hasattr(request, 'whitelisted')
    
def is_brownlisted(request):
    return hasattr(request, 'brownlisted')    