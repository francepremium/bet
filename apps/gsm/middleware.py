import pytz, datetime

from timezones.utils import adjust_datetime_to_timezone

class TimezoneMiddleware(object):
    def process_request(self, request):
        request.timezone = request.session.get('timezone', {})
        print request.timezone, request.session.get('timezone', False)
        
        if not request.timezone.keys() and request.user.is_authenticated():
            request.timezone['string'] = request.user.account_set.all()[0].timezone

            ref = datetime.datetime.now()
            timezone = pytz.timezone(request.timezone['string'])            
            request.timezone['offset'] = timezone.utcoffset(ref).seconds / 3600
            request.timezone['timezone'] = timezone
