def user_role(request):
<<<<<<< HEAD
    """
    Add user role to template context for easy access in templates.
    """
    role = None
    if request.user.is_authenticated:
        role = request.user.role
    return {"user_role": role}
    
=======
    role = None
    if request.user.is_authenticated:
        role = request.user.role
    return {"user_role": role}
>>>>>>> 5a1a3e867c88f623617f14ff6f950e7e72a946c0
