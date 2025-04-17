from datetime import timedelta
from django.utils import timezone
from admin_panel.models import DailyCheckIn

def perform_daily_checkin(user):
    today = timezone.now().date()

    # Already checked in today
    if DailyCheckIn.objects.filter(user=user, date=today).exists():
        return {'status': 'already_checked_in'}

    # Get yesterday's check-in
    yesterday = today - timedelta(days=1)
    yesterday_checkin = DailyCheckIn.objects.filter(user=user, date=yesterday).first()

    if yesterday_checkin:
        # Continue the streak
        streak = yesterday_checkin.streak_count + 1
    else:
        # Start a new streak
        streak = 1

    # Create today’s check-in
    DailyCheckIn.objects.create(user=user, streak_count=streak)

    return {
        'status': 'checked_in',
        'streak': streak
    }
