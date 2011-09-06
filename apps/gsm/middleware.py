import pytz, datetime

from django import http
from django import template
from django.template import loader
from django.conf import settings
from timezones.utils import adjust_datetime_to_timezone

class TimezoneMiddleware(object):
    def process_request(self, request):
        request.timezone = request.session.get('timezone', {})
        
        if not request.timezone.keys():
            if request.user.is_authenticated():
                request.timezone['string'] = request.user.account_set.all()[0].timezone
            else:
                request.timezone['string'] = settings.TIME_ZONE

            ref = datetime.datetime.now()
            timezone = pytz.timezone(request.timezone['string'])            
            request.timezone['offset'] = timezone.utcoffset(ref).seconds / 3600
            request.timezone['timezone'] = timezone
