from django.contrib.auth.models import User

from datetime import datetime


def user_role_in_ride(user, ride):
    """Return the user's role in the ride"""
    if ride.owner.id == user.id:
        return 'owner'
    elif ride.driver is not None and ride.driver.id == user.id:
        return 'driver'
    # elif User.objects.filter(rides_as_sharer__id=ride.id, id=user.id).exists():
    #     user_role = 'sharer'
    elif user in ride.sharers.all():
        return 'sharer'
    else:
        return 'other'


def str_to_datetime(string):
    """Translate a string to datetime"""
    """String in format: Jan. 1, 2019, 12:12 p.m."""
    string = string.replace('.', '')
    for fmt in ('%b %d, %Y, %I:%M %p', '%B %d, %Y, %I:%M %p'):
        try:
            return datetime.strptime(string, fmt)
        except ValueError:
            pass
    raise ValueError('no valid date format found')
