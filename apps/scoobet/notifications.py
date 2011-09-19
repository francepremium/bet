import time
import datetime

from redis import Redis

from django import http
from django.contrib.comments.models import Comment
from django.contrib.comments.signals import comment_was_posted
from django.utils import simplejson

from subscription.models import Subscription
from subscription_backends import RedisBackend

def acknowledge(request):
    if not request.user.is_authenticated():
        return {}
    
    if 'acknowledge' in request.GET.keys():
        b = RedisBackend()
        b.acknowledge(request.user, request.GET['acknowledge'])

    return {}

def user_stream_json(request):
    if not request.user.is_authenticated():
        return http.HttpResponseForbidden()

    b = RedisBackend()
    context = b.user_fetch(request.user, clear_undelivered=True)
    
    for g in context.keys():
        for v  in context[g]:
            del v['datetime']
        # oldest first
        context[g].reverse()

    return http.HttpResponse(simplejson.dumps(context))

def auto_subscribe(sender, **kwargs):
    comment = kwargs.pop('comment')
    Subscription.objects.subscribe(comment.user,comment.content_object)
comment_was_posted.connect(auto_subscribe, sender=Comment)

def emit_new_comment(comment):
    Subscription.objects.emit(
        u'%(actor)s commented on %(target)s',
        subscribers_of=comment.content_object,
        dont_send_to=[comment.user],
        format_kwargs={
            'comment': comment,
        },
        actor=comment.user,
        kind='comment',
    )
