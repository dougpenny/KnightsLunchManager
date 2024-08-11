from functools import wraps


def admin_access_allowed(func):
    """
    Decorator for views that checks that the user is a memeber of the
    admin staff group in Django Admin. If not, the user is redirected
    to the 'home' page for the site and a warning message is displayed.
    """

    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_staff:
            return func(request, *args, **kwargs)
        else:
            from django.contrib import messages

            messages.warning(request, "You do not have permission to access this page.")
            from django.shortcuts import redirect

            return redirect("home")

    return wrapper
