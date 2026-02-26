from django.shortcuts import redirect, reverse
from django.contrib import messages
from django.http import HttpResponse

def role_required(allowed_roles=[]):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            if request.user.role not in allowed_roles:
                return view_func(request, *args, **kwargs)
        else:
             return HttpResponse("You do not have permission to access this page.")
        return wrapper
    return decorator
    