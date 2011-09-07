from django import http
from django import template
from django.template import loader
from django.conf import settings

import gsm
import scoobet

class ExceptionMiddleware(object):
    def process_exception(self, request, exception):
        if settings.DEBUG:
            return None

        if exception.__class__.__name__ not in settings.EXCEPTION_MIDDLEWARE_HANDLES:
            return None

        context = {
            'error': exception.__class__.__name__,
            'exception': exception,
        }

        response = http.HttpResponse(
            loader.render_to_string(
                'error.html',
                context,
                context_instance=template.RequestContext(request)
            ),
            status=504
        )
        response['Retry-After'] = 5*60
        return response
