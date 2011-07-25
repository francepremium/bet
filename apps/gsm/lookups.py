import datetime

from django.db.models import Q

from models import *

class SessionLookup(object):
    def get_query(self, q, request):
        qs = Session.objects.filter(
            datetime_utc__gte=datetime.datetime.now(),
            datetime_utc__lte=datetime.datetime.now() + datetime.timedelta(20)
        ).filter(
            Q(name_ascii__icontains=q)
        )
        if 'sport' in request.GET:
            qs = qs.filter(sport__pk=request.GET['sport'])
        return qs

    def format_result(self, session):
        return '%s <span>%s</span>' % (
            session.name,
            session.sport.name,
        )

    def format_item(self, session):
        return session.name

    def get_objects(self, ids):
        return Session.objects.filter(pk__in=ids)
