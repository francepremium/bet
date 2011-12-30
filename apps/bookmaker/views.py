from django.db.models import Q, Sum
from django.utils import simplejson
from django.utils.translation import ugettext as _
from django import template
from django import http
from django import shortcuts
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.forms.models import inlineformset_factory

from bet.helpers import *
from filters import *
from models import *
from forms import *

def bet_types_json(request,
    qs=BetType.objects.all()):
    if request.GET.get('sport'):
        qs = qs.filter(sport__name__icontains=request.GET['sport'])
    if request.GET.get('bookmaker'):
        qs = qs.filter(bookmaker__pk=request.GET['bookmaker'])
    
    results = []
    for bettype in qs.select_related():
        results.append((bettype.pk, bettype.name))

    return http.HttpResponse(simplejson.dumps(results))

@login_required
def choices_for_bettype(request, qs=BetChoice.objects.all()):
    if request.GET.get('bettype'):
        qs = qs.filter(bettype__pk=request.GET.get('bettype'))

    results = []
    for betchoice in qs:
        results.append((betchoice.pk, betchoice.name))

    return http.HttpResponse(simplejson.dumps(results))

@login_required
def bet_types(request, pk, form_class=BookmakerForm,
    template_name='bookmaker/bet_types.html', extra_context=None):
    context = { 'is_admin': True, }

    bookmaker = shortcuts.get_object_or_404(Bookmaker, pk=pk)
    if not request.user.is_staff:
        if request.user.bookmaker != bookmaker:
            return http.HttpResponseForbidden()
    context['bookmaker'] = bookmaker

    if request.method == 'POST':
        form = form_class(request.POST, instance=bookmaker)
        if form.is_valid():
            form.save()
            messages.success(request, _(u'bookmaker profile updated'))
    else:
        form = form_class(instance=bookmaker)

    context['form'] = form
    context.update(extra_context or {})
    return shortcuts.render_to_response(template_name, context,
        context_instance=template.RequestContext(request))

@login_required
def edit(request, pk, form_class=BookmakerForm,
    template_name='bookmaker/form.html', extra_context=None):
    context = { 'is_admin': True, }

    bookmaker = shortcuts.get_object_or_404(Bookmaker, pk=pk)
    if not request.user.is_staff:
        if request.user.bookmaker != bookmaker:
            return http.HttpResponseForbidden()
    context['bookmaker'] = bookmaker

    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, instance=bookmaker)
        if form.is_valid():
            form.save()
            messages.success(request, _(u'bookmaker profile updated'))
    else:
        form = form_class(instance=bookmaker)

    context['form'] = form
    context.update(extra_context or {})
    return shortcuts.render_to_response(template_name, context,
        context_instance=template.RequestContext(request))

def detail(request, pk, tab='home',
    template_name='bookmaker/%s.html', extra_context=None):
    context = {}
    context['bookmaker'] = bookmaker = shortcuts.get_object_or_404(Bookmaker, pk=pk)
    try:
        if request.user.is_authenticated():
            context['is_admin'] = request.user.bookmaker == bookmaker or request.user.is_staff
    except Bookmaker.DoesNotExist:
        context['is_admin'] = False
    context['bookmaker'] = bookmaker

    if tab == 'picks':
        context['bet_list_helper'] = BetListHelper(request, ticket__bookmaker=bookmaker, exclude_filters=['sport', 'bettype', 'competition', 'has_text', 'has_upload'])

    context.update(extra_context or {})
    return shortcuts.render_to_response(template_name % tab, context,
        context_instance=template.RequestContext(request))

def file(request, pk,
    template_name='bookmaker/file.html', extra_context=None):
    context = {}
    bookmaker = shortcuts.get_object_or_404(Bookmaker, pk=pk)
    if request.user.is_authenticated():
        try:
            context['is_admin'] = request.user.bookmaker == bookmaker
        except Bookmaker.DoesNotExist:
            context['is_admin'] = request.user.is_staff
    context['bookmaker'] = bookmaker
    context['bookmaker_bettypes_per_sport'] = []
    previous_sport = None

    for bettype in bookmaker.bettype.all():
        if previous_sport != bettype.sport:
            current = {
                'sport': bettype.sport,
                'bettypes': []
            }
            context['bookmaker_bettypes_per_sport'].append(current)

        current['bettypes'].append(bettype)
        previous_sport = bettype.sport

    context.update(extra_context or {})
    return shortcuts.render_to_response(template_name, context,
        context_instance=template.RequestContext(request))

@login_required
def list_bet_type(request, pk,
    template_name='bookmaker/list_bet_type.html', extra_context=None):
    context = { 'is_admin': True, }

    bookmaker = shortcuts.get_object_or_404(Bookmaker, pk=pk)
    if not request.user.is_staff:
        if request.user.bookmaker != bookmaker:
            return http.HttpResponseForbidden()
    context['bookmaker'] = bookmaker

    qs = BetType.objects.all()
    context['filter'] = BetTypeFilter(request.GET, qs)

    context.update(extra_context or {})
    return shortcuts.render_to_response(template_name, context,
        context_instance=template.RequestContext(request))

@login_required
def add_bet_type(request, pk,
    form_class=BetTypeForm,
    template_name='bookmaker/form.html', extra_context=None):
    bookmaker = shortcuts.get_object_or_404(Bookmaker, pk=pk)
    if not request.user.is_staff:
        if request.user.bookmaker != bookmaker:
            return http.HttpResponseForbidden()

    context = {
        'bookmaker': bookmaker,
        'is_admin': True,
    }

    if request.method == 'POST':
        form = context['form'] = form_class(request.POST)
        if form.is_valid():
            bettype = form.save(commit=False)
            if request.user.bookmaker:
                bettype.creation_bookmaker = request.user.bookmaker
            bettype.save()
            if request.user.bookmaker:
                request.user.bookmaker.bettype.add(bettype)
                messages.success(request, _(u'bet type %(bettype)s created and assigned to bookmaker %(bookmaker)s') % {
                    'bettype': bettype,
                    'bookmaker': bookmaker,
                })
            else:
                messages.success(request, _(u'bet type %s created' % bettype))
            return shortcuts.redirect(urlresolvers.reverse(
                'bookmaker_edit_bet_type', args=(bookmaker.pk, bettype.pk)))
    else:
        form = context['form'] = form_class()

    context.update(extra_context or {})
    return shortcuts.render_to_response(template_name, context,
        context_instance=template.RequestContext(request))

@login_required
def edit_bet_type(request, pk, bettype_pk, form_class=BetTypeForm,
    template_name='bookmaker/edit_bet_type.html', extra_context=None):
    bookmaker = shortcuts.get_object_or_404(Bookmaker, pk=pk)
    if request.user.bookmaker != bookmaker and not request.user.is_staff:
        return http.HttpResponseForbidden()

    context = {
        'bookmaker': bookmaker,
        'is_admin': True,
    }

    bettype = shortcuts.get_object_or_404(BetType, pk=bettype_pk)

    creator = request.user.bookmaker == bettype.creation_bookmaker
    only_user = [request.user.bookmaker] == list(bettype.bookmaker_set.all())
    allowed = creator or only_user or request.user.is_staff
    if not allowed:
        return http.HttpResponseForbidden()

    formset_class = inlineformset_factory(BetType, BetChoice,
        fields=('name_fr', 'name_en'))

    if request.method == 'POST':
        form = context['form'] = form_class(request.POST, instance=bettype)
        formset = context['formset'] = formset_class(request.POST, instance=bettype)
        if form.is_valid():
            bettype = form.save()
        if formset.is_valid():
            choices = formset.save()
        if form.is_valid() and formset.is_valid():
            messages.success(request, _(u'bet type %s updated' % bettype))
            return shortcuts.redirect(urlresolvers.reverse(
                'bookmaker_edit_bet_type', args=(bookmaker.pk, bettype.pk)))
    else:
        form = context['form'] = form_class(instance=bettype)
        formset = context['formset'] = formset_class(instance=bettype)

    context.update(extra_context or {})
    return shortcuts.render_to_response(template_name, context,
        context_instance=template.RequestContext(request))

@login_required
def change_bet_type(request, pk):
    bookmaker = shortcuts.get_object_or_404(Bookmaker, pk=pk)
    if not request.user.is_staff:
        if request.user.bookmaker != bookmaker:
            return http.HttpResponseForbidden()

    if request.method != 'POST':
        return http.HttpResponseBadRequest()

    bettype = shortcuts.get_object_or_404(BetType, pk=request.POST['pk'])

    if request.POST['action'] == 'add':
        if bookmaker.bettype.filter(pk=bettype.pk).count() > 0:
            msg = _('bookmaker %s already supports bet type: no need to add') % (
                bookmaker,
                bettype
            )
            status=409
        else:
            msg = _('successfully added bet type %(bettype)s to bookmaker %(bookmaker)s') % {
                'bettype': bettype,
                'bookmaker': bookmaker,
            }
            bookmaker.bettype.add(bettype)
            status = 201
    else:
        if bookmaker.bettype.filter(pk=bettype.pk).count() > 0:
            msg = _('successfully removed bet type %(bettype)s from bookmaker %(bookmaker)s') % {
                'bettype': bettype,
                'bookmaker': bookmaker,
            }
            status = 201
            bookmaker.bettype.remove(bettype)
        else:
            msg = _('bookmaker %(bookmaker)s does not bet type %(bettype)s: no need to remove') % {
                'bookmaker': bookmaker,
                'bettype': bettype
            }
            status = 409

    return http.HttpResponse(msg, status=status)
