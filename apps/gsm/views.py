from django import template
from django import http
from django import shortcuts
from django.conf import settings
from django.utils.translation import get_language_from_request

from models import *

import gsm

def entity_list(request, sport, tag, 
    update=False,
    template_name='', extra_context=None):

    if sport not in [x for x, y in settings.SPORTS]:
        return http.HttpResponseBadRequest()

    template_name = (
        template_name,
        'gsm/%s/%s_list.html' % (sport, tag),
        'gsm/%s_list.html' % tag,
    )

    context = {
        'sport': sport,
        'language': get_language_from_request(request),
    }

    context['tree'] = gsm.get_tree(
        context['language'], 
        sport,
        'get_%ss' % tag,
        update=update
    )

    context.update(extra_context or {})
    return shortcuts.render_to_response(template_name, context,
        context_instance=template.RequestContext(request))

def entity_detail(request, sport, tag, gsm_id,
    update=True,
    template_name='', extra_context=None):

    if sport not in [x for x, y in settings.SPORTS]:
        return http.HttpResponseBadRequest()

    template_name = (
        template_name,
        'gsm/%s/%s_detail.html' % (sport, tag),
        'gsm/%s_detail.html' % tag,
    )

    context = {
        'sport': sport,
        'language': get_language_from_request(request),
    }

    entity, created = GsmEntity.objects.get_or_create(
        sport = sport,
        tag = tag,
        gsm_id = gsm_id
    )
    context['entity'] = entity

    context.update(extra_context or {})
    return shortcuts.render_to_response(template_name, context,
        context_instance=template.RequestContext(request))

def sport_detail(request, sport, tab,
    template_name='', extra_context=None):

    template_name = (
        template_name
        'gsm/sport/%s.html' % tab,
    )

    context.update(extra_context or {})
    return shortcuts.render_to_response(template_name, context,
        context_instance=template.RequestContext(request))
