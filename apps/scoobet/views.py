from django.db.models import Q
from django.utils.translation import ugettext as _
from django import template
from django import http
from django import shortcuts
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from endless_pagination.decorators import page_template
from django.core import urlresolvers

from actstream.models import actor_stream, Follow

@login_required
def me(request):
    return shortcuts.redirect(urlresolvers.reverse(
        'user_detail', args=(request.user.username,)))

def user_detail(request, username, tab='activities',
    template_name='auth/user_%s.html', extra_context=None):

    context = {}

    user = context['object'] = shortcuts.get_object_or_404(User, 
                                                        username=username)

    if request.user == user:
        context['is_me'] = True
    
    if tab == 'activities':
        context['activity_list'] = actor_stream(user)
        context['page_template'] = 'auth/user_activities_page.html'
    elif tab == 'social':
        context['follower_list'] = user.follows()
        context['following_list'] = user.following()
        if context['follower_list'].count() > context['following_list'].count():
            context['paginate_list'] = context['follower_list']
        else:
            context['paginate_list'] = context['following_list']
        context['page_template'] = 'auth/user_social_page.html'

    if request.is_ajax() and 'page_template' in context.keys():
        template_name = context['page_template']
    else:
        template_name = template_name % tab

    context.update(extra_context or {})
    return shortcuts.render_to_response(template_name, context,
        context_instance=template.RequestContext(request))
