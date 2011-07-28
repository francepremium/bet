import pytz, datetime

from timezones.utils import adjust_datetime_to_timezone

def available_timezones(request):
    return {
        'available_timezones': range(-12, 13),
    }


