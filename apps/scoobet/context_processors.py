from django_messages.models import inbox_count_for

def inbox_count(request):
    context = {}

    if request.user.is_authenticated():
        context['inbox_count'] = inbox_count_for(request.user)

    return context
