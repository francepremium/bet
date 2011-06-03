from django.core import urlresolvers

from models import *

def incomplete_ticket(request):
    if not request.user.is_authenticated():
        return {}
    
    tickets = request.user.ticket_set.filter(status=TICKET_STATUS_INCOMPLETE).order_by('-pk').values_list('pk', flat=True)
    if len(list(tickets)):
        return {
            'incomplete_ticket_url': urlresolvers.reverse('bet_form', 
                args=(tickets[0],))
        }
    
    return {}
