from django.db.models import Q
from django.utils.translation import ugettext as _
from django import template
from django import http
from django import shortcuts
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views import generic

from models import *
from forms import *
from filters import *

@login_required
def clan_form(request, form_class=ClanForm,
    template_name='clan/clan_form.html', extra_context=None):
    context = {}

    pk = request.GET.get('pk', False)
    if pk:
        context['clan'] = clan = shortcuts.get_object_or_404(Clan, pk=pk)
    else:
        context['clan'] = clan = Clan(creation_user=request.user)

    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, instance=clan)
        if form.is_valid():
            clan = form.save()
            messages.success(request, _(u'clan %s created') % clan)
            return shortcuts.redirect(clan.get_absolute_url())
    else:
        form = form_class(instance=clan)
    context['form'] = form

    context.update(extra_context or {})
    return shortcuts.render_to_response(template_name, context,
        context_instance=template.RequestContext(request))

@login_required
def clan_join(request, slug,
    template_name='clan/clan_join.html', extra_context=None):
    context = {}
    context['clan'] = clan = shortcuts.get_object_or_404(Clan, slug=slug)

    if clan.has_waiting_user(request.user):
        messages.error(request, _('you already have a pending application to clan %s') % clan)
        return shortcuts.redirect(clan.get_absolute_url())

    if clan.has_user(request.user):
        messages.error(request, _('you are already part of clan %s') % clan)
        return shortcuts.redirect(clan.get_absolute_url())

    membership = Membership(user=request.user, clan=clan)
    membership.save()
    
    if clan.auto_approve:
        messages.success(request, _('you have joined clan %s') % clan)
    else:
        messages.success(request, _('you have requested to join clan %s. A clan administrator will approve or reject your application') % clan)

    return shortcuts.redirect(clan.get_absolute_url())

@login_required
def clan_quit(request, slug,
    template_name='clan/clan_quit.html', extra_context=None):
    context = {}
    context['clan'] = clan = shortcuts.get_object_or_404(Clan, slug=slug)

    if not clan.has_user(request.user) and not clan.has_waiting_user(request.user):
        messages.error(request, _('you are not part of clan %s') % clan)
        return shortcuts.redirect(clan.get_absolute_url())
    
    if clan.is_admin(request.user) and clan.membership_set.filter(kind=0).count() < 2:
        messages.error(request, _('you may not leave clan %s because you are the only admin') % clan)
        return shortcuts.redirect(clan.get_absolute_url())

    if clan.has_waiting_user(request.user):
        message = _('you have canceled application to clan %s') % clan
    else:
        message = _('you have quit clan %s') % clan
    
    membership = Membership.objects.filter(user=request.user, clan=clan).delete()
    messages.success(request, message)
    return shortcuts.redirect(clan.get_absolute_url())

@login_required
def clan_admin(request, slug,
    template_name='clan/clan_admin.html', extra_context=None):
    context = {}
    context['clan'] = clan = shortcuts.get_object_or_404(Clan, slug=slug)

    if not clan.is_admin(request.user):
        messages.error(request, _('you are not an administrator of clan %s') % clan)
        return shortcuts.redirect(clan.get_absolute_url())

    membership = shortcuts.get_object_or_404(Membership, pk=request.GET.get('membership', None))
    if clan.is_admin(membership.user):
        messages.error(request, _('you may not kick an admin, he must quit by himself'))
        return shortcuts.redirect(clan.get_absolute_url())

    if request.GET.get('do') in ('reject', 'exclude'):
        membership.delete()
        if request.GET.get('do') == 'reject':
            messages.success(request, _('rejected application of %s') % membership.user)
        else:
            messages.success(request, _('excluded %s') % membership.user)
    elif request.GET.get('do') in ('promote', 'approve'):
        if request.GET.get('do') == 'promote':
            membership.kind = 0
            messages.success(request, _('promoted %s') % membership.user)
        else:
            membership.kind = 1
            messages.success(request, _('approved %s') % membership.user)
        membership.save()
    else:
        return http.HttpResponseBadRequest('You found an horrible bug which should not happen (missing or unsupported "do" in the url)')
    
    return shortcuts.redirect(clan.get_absolute_url())
