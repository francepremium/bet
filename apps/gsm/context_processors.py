import pytz, datetime

from timezones.utils import adjust_datetime_to_timezone

from gsm.templatetags.gsm_tags import timezone_adjust

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
