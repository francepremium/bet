from django.db import connection, transaction
from django.db import models
from django.db.models import signals
from django.utils.translation import ugettext as _
from django.core import urlresolvers
from django.template import defaultfilters
from django.conf import settings
from django.core.cache import cache

import autoslug

class Article(models.Model):
    name = models.CharField(max_length=100, verbose_name=_(u'title'))
    slug = autoslug.AutoSlugField(populate_from='name', unique=True)
    
    creation_user = models.ForeignKey('auth.User')
    creation_datetime = models.DateTimeField(auto_now_add=True)
    modification_datetime = models.DateTimeField(auto_now=True)

    text = models.TextField()

    def __unicode__(self):
        return self.name
    
    def get_absolute_url(self):
        return urlresolvers.reverse('article_detail', args=(self.slug,))


if 'actstream' in settings.INSTALLED_APPS:
    import actstream

    def article_save(sender, **kwargs):
        if not kwargs.get('created', False):
            actstream.action.send(kwargs['instance'].creation_user, 
                verb='updated article', action_object=kwargs['instance'])
        else:
            actstream.action.send(kwargs['instance'].creation_user, 
                verb='created article', action_object=kwargs['instance'])
    signals.post_save.connect(article_save, sender=Article)
