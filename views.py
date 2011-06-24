from django.db.models import Q
from django.utils.translation import ugettext as _
from django import template
from django import http
from django import shortcuts
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views import generic

from gsm.models import *
from bookmaker.models import *
from bet.models import *

def session_bettype_detail(request, session_pk, bettype_pk,
    template_name='session_bettype_detail.html', extra_context=None):
    context = {}

    bettype = context['bettype'] = shortcuts.get_object_or_404(BetType,
                                                                pk=bettype_pk)
    session = context['session'] = shortcuts.get_object_or_404(Session,
                                                                pk=session_pk)

    bet_list = context['bet_list'] = Bet.objects.filter(bettype=bettype,
                                                        session=session)

    choice_counts = context['choice_counts'] = {}
    for choice in bettype.betchoice_set.all():
        choice_counts[choice.name] = bet_list.filter(choice=choice).count()
   
    total_bets = context['total_bets'] = bet_list.count()
    
    choice_percents = context['choice_percents'] = {}
    for choice, count in choice_counts.items():
        choice_percents[choice] = ( float(count)  / total_bets ) * 100

    argumented_bets = context['argumented_bets'] = bet_list.exclude(
        text='', upload='').order_by('-pk')

    context['page_template'] = 'session_bettype_detail_page.html'
    if request.is_ajax() and 'page_template' in context.keys():
        template_name = context['page_template']

    context.update(extra_context or {})
    return shortcuts.render_to_response(template_name, context,
        context_instance=template.RequestContext(request))

# mega hollidays hack
import subprocess
def git_pull(request):
    output = subprocess.check_output(['git', 'pull', 'origin', 'master'])
    return http.HttpResponse(output)
