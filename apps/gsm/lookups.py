import datetime

from django.db.models import Q

from models import *

class SessionLookup(object):
    def get_query(self, q, request):
        qs = Session.objects.filter(
            start_datetime__gt=datetime.datetime.now()
        ).filter(
            Q(name_ascii__icontains=q)
        ).order_by('start_datetime')
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
