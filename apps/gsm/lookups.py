import datetime

from django.db.models import Q

from models import *

class SessionLookup(object):
    def get_query(self, q, request):
        qs = Session.objects.filter(
            datetime_utc__gte=datetime.datetime.now(),
            datetime_utc__lte=datetime.datetime.now() + datetime.timedelta(20)
        ).filter(
            Q(oponnent_A_name__istartswith=q) | 
            Q(oponnent_B_name__istartswith=q)
        )
        if 'sport' in request.GET:
            qs = qs.filter(sport__pk=request.GET['sport'])
        return qs

    def format_result(self, session):
        return "%s vs. %s" % (
            session.oponnent_A_name,
            session.oponnent_B_name,
        )

    def format_item(self, session):
        return "%s vs. %s" % (
            session.oponnent_A_name,
            session.oponnent_B_name,
        )

    def get_objects(self, ids):
        return Session.objects.filter(pk__in=ids)
