import time
import datetime

from django.conf import settings
from django.utils import simplejson

from redis import Redis
from subscription import backends
from localeurl.utils import locale_url, strip_path

class BaseBackend(backends.BaseBackend):
    def get_user_language_code(self, user):
        account = user.account_set.all()[0]
        return account.language

    def process_user_format_kwargs(self, actor, text, user, format_kwargs):
        t = self.get_user_translation(user)
        l = self.get_user_language_code(user)

        target_html = '<a href="%(url)s" class="acknowledge">%(name)s</a>'
        target_context = {}

        if 'comment' in format_kwargs.keys():
            content = format_kwargs['comment'].content_object

            target_context['url'] = locale_url(strip_path(content.get_absolute_url())[1], l)

            attr = 'name_%s' % l
            if hasattr(content, attr):
                target_context['name'] = getattr(content, attr)
            elif content.__class__.__name__ == 'Action':
                if content.actor == user:
                    target_context['name'] = t.gettext('your action')
                else:
                    target_context['name'] = '%s\'s action' % actor.username

            format_kwargs['target'] = target_html % target_context
        return format_kwargs

class RedisBackend(BaseBackend):
    def serialize(self, user, text, **kwargs):
        return simplejson.dumps({
            # i didn't understand the originnal date code ...
            'timestamp': time.mktime(datetime.datetime.now().timetuple()),
            'text': text,
            'kwargs': kwargs,
        })

    def unserialize(self, data):
        data = simplejson.loads(data)
        data['datetime'] = datetime.datetime.fromtimestamp(data['timestamp'])
        return data

    def acknowledge(self, user, timestamp):
        conn = Redis()

        if hasattr(user, 'pk'):
            user = user.pk

        unacknowledged = conn.lrange('actstream::%s::unacknowledged' % user, 0, -1)
        for u in unacknowledged:
            a = self.unserialize(u)
            if float(a['timestamp']) == float(timestamp):
                conn.lrem('actstream::%s::unacknowledged' % user, u, 1)
                conn.lpush('actstream::%s::acknowledged' % user, u)
                break

    def user_fetch(self, user, clear_undelivered=False):
        conn = Redis()

        if clear_undelivered:
            undelivered = conn.lrange("actstream::%s::undelivered" % user.pk,0,-1)
            for u in undelivered:
                conn.lpush("actstream::%s::unacknowledged" % user.pk,u)

            conn.delete("actstream::%s::undelivered" % user.pk)

        groups = {}
        for k in ('acknowledged', 'unacknowledged', 'undelivered'):
            groups[k] = [self.unserialize(x) for x in conn.lrange("actstream::%s::%s" % (user.pk, k),0,-1)]
        return groups

    def user_emit(self,user,text,**kwargs):
        conn = Redis()
        item = self.serialize(user, text, **kwargs)
        conn.lpush("actstream::%s::undelivered" % user.pk,item)
