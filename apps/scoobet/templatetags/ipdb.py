from django import template

register = template.Library()

@register.filter(name='ipdb')
def do_ipdb(value):
    import ipdb; ipdb.set_trace()
