from django.contrib.auth.models import User

from .models import DriverProfile


def is_email(email):
    """Verify an email address is valid in syntax"""
    from django.core.exceptions import ValidationError
    from django.core.validators import EmailValidator

    validator = EmailValidator()
    try:
        validator(email)
    except ValidationError:
        return False

    return True


def get_user_by_request(request):
    """
    USED WHEN THE USER IS AUTHENTICATED
    Return the user object
    """
    return User.objects.get(id=request.user.id)


def get_driver_profile_by_request(request):
    """
    USED WHEN THE USER IS AUTHENTICATED
    Return the user's driver profile
    """
    user = get_user_by_request(request)
    return DriverProfile.objects.get(user=user)


def is_driver(request):
    """
    USED WHEN THE USER IS AUTHENTICATED
    Return the user's is_driver field from his driver profile
    """
    return get_driver_profile_by_request(request).is_driver


def get_checkbox_input(input_name, request):
    """Get bootstrap checkbox input from a POST request"""
    if request.POST.get(input_name):
        return True
    else:
        return False

