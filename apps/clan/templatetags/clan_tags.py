from django import template

register = template.Library()

@register.filter
def is_clan_admin(clan, user):
    return clan.is_admin(user)

@register.filter
def has_clan_user(clan, user):
    return clan.has_user(user)

@register.filter
def has_clan_waiting_user(clan, user):
    return clan.has_waiting_user(user)
