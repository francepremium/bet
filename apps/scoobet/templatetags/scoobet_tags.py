from django import template

import scoobet

register = template.Library()

@register.filter
def group_activities(activities):
    return scoobet.group_activities(activities)

@register.inclusion_tag('auth/_includes/user_list.html')
def render_user_list(request, user_list):
    return {
        'request': request,
        'user_list': user_list,
    }
