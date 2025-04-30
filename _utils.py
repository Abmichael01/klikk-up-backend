from datetime import timedelta
from django.utils import timezone


def format_time_since(date):
    """
    Returns a human-readable string representing the time difference
    between the current time and the given date.
    """
    now = timezone.now()
    diff = now - date

    # If the difference is less than a day, show time relative to the current time
    if diff < timedelta(minutes=1):
        return "Just now"
    elif diff < timedelta(hours=1):
        minutes = diff.seconds // 60
        return f"{minutes} min{'s' if minutes > 1 else ''} ago"
    elif diff < timedelta(days=1):
        hours = diff.seconds // 3600
        return f"{hours} hr{'s' if hours > 1 else ''} ago"
    elif diff < timedelta(days=2):
        return "Yesterday"
    elif diff < timedelta(weeks=1):
        days = diff.days
        return f"{days} day{'s' if days > 1 else ''} ago"
    elif diff < timedelta(weeks=2):
        return "1 wk ago"
    else:
        weeks = diff.days // 7
        return f"{weeks} wk{'s' if weeks > 1 else ''} ago"
