from django.db import connection, transaction
from django.db import models
from django.db.models import signals
from django.utils.translation import ugettext as _
from django.core import urlresolvers
from django.template import defaultfilters
from django.conf import settings
from django.core.cache import cache

import autoslug

class Clan(models.Model):
    CLAN_KIND_CHOICES = (
        (0, _(u'public')),
        (1, _(u'semi-private')),
        (2, _(u'private')),
    )
    
    def image_upload_to(instance, filename):
        return 'clan/%s/%s' % (instance.pk, filename)

    creation_user = models.ForeignKey('auth.User', related_name='created_clan_set')
    creation_datetime = models.DateTimeField(auto_now_add=True)
    modification_datetime = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=100)
    slug = autoslug.AutoSlugField(populate_from='name', unique=True)
    auto_approve = models.BooleanField(default=False)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to=image_upload_to, blank=True)
    kind = models.IntegerField(choices=CLAN_KIND_CHOICES)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return urlresolvers.reverse('clan_detail', args=(self.slug,))

    def has_user(self, user):
        if not user.is_authenticated(): 
            return False
        return Membership.objects.filter(user=user, clan=self,
            kind__isnull=False).count() > 0

    def is_admin(self, user):
        if not user.is_authenticated(): 
            return False
        return Membership.objects.filter(user=user, clan=self,
            kind=0).count() > 0

    def has_waiting_user(self, user):
        if not user.is_authenticated(): 
            return False
        return Membership.objects.filter(user=user, clan=self,
            kind__isnull=True).count() > 0

    @property
    def active_membership_set(self):
        return self.membership_set.filter(kind__isnull=False)

    @property
    def pending_membership_set(self):
        return self.membership_set.filter(kind__isnull=True)

    @property
    def active_membership_set_per_kind(self):
        """
        Returns a list with one dict per kind:
        [ 
            (
                kind display name, 
                Membership list
            )
        ]
        """
        data = []
        for kind, kind_display in Membership._meta.get_field('kind').choices:
            data.append((
                kind_display, 
                Membership.objects.filter(kind=kind, clan=self)
            ))
        return data

def clan_non_public_do_not_auto_approve(sender, **kwargs):
    if kwargs['instance'].kind == 0:
        kwargs['instance'].auto_approve = True
signals.pre_save.connect(clan_non_public_do_not_auto_approve, sender=Clan)

def clan_creation_user_to_admin_member(sender, **kwargs):
    if kwargs['created']:
        Membership(user=kwargs['instance'].creation_user,
            clan=kwargs['instance'], kind=0).save()
signals.post_save.connect(clan_creation_user_to_admin_member, sender=Clan)

class Membership(models.Model):
    CLAN_MEMBERSHIP_KIND_CHOICES = (
        (0, _(u'administrator')),
        (1, _(u'member')),
    )

    user = models.ForeignKey('auth.User')
    clan = models.ForeignKey('Clan')

    creation_datetime = models.DateTimeField(auto_now_add=True)

    modification_datetime = models.DateTimeField(auto_now=True)
    modification_user = models.ForeignKey('auth.User', related_name='approved_membership_set', null=True)
    kind = models.IntegerField(choices=CLAN_MEMBERSHIP_KIND_CHOICES, null=True, default=None)

    class Meta:
        ordering = ('clan', 'kind')
        unique_together = ('user', 'clan')

def membership_auto_approve(sender, **kwargs):
    if kwargs['instance'].clan.auto_approve:
        kwargs['instance'].kind = 1
signals.pre_save.connect(membership_auto_approve, sender=Membership)
