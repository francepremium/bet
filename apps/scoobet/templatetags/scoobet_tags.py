from django import template

register = template.Library()

@register.inclusion_tag('auth/_includes/user_list.html')
def render_user_list(request, user_list):
    return {
        'request': request,
        'user_list': user_list,
    }
