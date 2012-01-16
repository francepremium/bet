import pytz, datetime

from timezones.utils import adjust_datetime_to_timezone

from django.db.models import Count

from gsm.models import Session
from gsm.templatetags.gsm_tags import timezone_adjust

def five_popular_sessions(request):
    qs = Session.objects.filter(status='Fixture').annotate(
        bet_count=Count('bet')).order_by('-bet_count').select_related(
            'sport', 'oponnent_A', 'oponnent_B')[:5]
    return {
        'five_popular_sessions': qs,
    }

def available_timezones(request):
    now = datetime.datetime.now()
    adjusted_now = timezone_adjust(request, now)
    choices = []
    for timezone in range(-12, 13):
        hour = now.hour + timezone
        if hour < 0:
            hour += 24
        choices.append({
            'timezone': timezone,
            'hour': hour,
        })

    return {
        'available_timezones': choices,
        'now': adjusted_now,
    }
