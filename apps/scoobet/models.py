from django.db.models import signals, Q
from django.utils.translation import ugettext as _
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.contrib.comments.models import Comment

from actstream import action
from actstream.models import Action, Follow
from django_messages.models import Message

import scoobet
# get_rankings monkey patch
import scoobet.rankings
# django-subscription configuration
import scoobet_subscriptions

def follow_betspire(sender, instance=None, **kwargs):
    if not kwargs['created']: return

    try:
        betspire = User.objects.get(username='betspire')
        follow = Follow(actor=betspire, user=instance)
        follow.save()
    except User.DoesNotExist:
        pass

signals.post_save.connect(follow_betspire, sender=User)

def user_messaging_security(sender, **kwargs):
    m = kwargs['instance']
    authorized = m.sender.following().filter(pk=m.recipient.pk).count() > 0
    if not authorized:
        raise scoobet.MessagingUnauthorizedUser(m)
signals.pre_save.connect(user_messaging_security, 
    sender=Message)

def user_registered_activity(sender, **kwargs):
    if not kwargs.get('created', False):
        return None
    action.send(kwargs['instance'], verb='registered')
signals.post_save.connect(user_registered_activity, 
    sender=User)

def delete_object_activities(sender, **kwargs):
    """
    This signal attempts to delete any activity which is related to Action
    through a generic relation. This should keep the Action table sane.
    """
    if sender.__name__ == 'Session':
        return None

    Action.objects.filter(
        action_object_object_id=kwargs['instance'].pk,
        action_object_content_type=ContentType.objects.get_for_model(
                                                        kwargs['instance'])
        ).delete()
    Action.objects.filter(
        actor_object_id=kwargs['instance'].pk,
        actor_content_type=ContentType.objects.get_for_model(
                                                        kwargs['instance'])
        ).delete()
    Action.objects.filter(
        target_object_id=kwargs['instance'].pk,
        target_content_type=ContentType.objects.get_for_model(
                                                        kwargs['instance'])
        ).delete()
signals.pre_delete.connect(delete_object_activities)

def comment_posted(sender, **kwargs):
    if not kwargs.get('created', False):
        return None

    comment = kwargs['instance']
    
    if not comment.user:
        return None

    if comment.user == comment.content_object:
        action.send(comment.user, verb='updated his status', action_object=comment)
    elif isinstance(comment.content_object, User):
        action.send(comment.user, verb='wall posted', action_object=comment, target=comment.content_object)
    else:
        action.send(comment.user, verb='commented', action_object=comment)
signals.post_save.connect(comment_posted, sender=Comment)

def unfollow_deletes_activity(sender, **kwargs):
    instance = kwargs['instance']
    actions = Action.objects.filter(
        actor_object_id = instance.user.pk,
        actor_content_type = instance.content_type,
        verb='started following',
        target_content_type = instance.content_type,
        target_object_id = instance.object_id
    )
    # trigger *_delete
    for a in actions:
        a.delete()
signals.pre_delete.connect(unfollow_deletes_activity, sender=Follow)

def new_action_unicode(self):
    if self.target:
        if self.action_object:
            return u'%s %s %s on %s' % (self.actor, self.verb, self.action_object, self.target)
        else:
            return u'%s %s %s' % (self.actor, self.verb, self.target)

    if self.action_object:
        return u'%s %s %s' % (self.actor, self.verb, self.action_object)

    return u'%s %s' % (self.actor, self.verb)
Action.__unicode__ = new_action_unicode

def user_friends(user):
    follows_users_ids = Follow.objects.filter(user=user,
                                              content_type__app_label='auth',
                                              content_type__model='user') \
                                      .exclude(object_id=user.pk) \
                                      .values_list('object_id', flat=True)
    c = ContentType.objects.get_for_model(User)
    target_choices_qs = User.objects.filter(
        Q(follow__object_id=user.pk, follow__content_type=c) | 
        Q(id__in=follows_users_ids)
    ).distinct()
    return target_choices_qs
User.friends = user_friends

def user_follows(user):
    c = ContentType.objects.get_for_model(User)

    follows_users_ids = Follow.objects.filter(user=user,
                                              content_type__app_label='auth',
                                              content_type__model='user') \
                                      .exclude(object_id=user.pk) \
                                      .values_list('object_id', flat=True)
    return User.objects.filter(pk__in=follows_users_ids).distinct()
User.follows = user_follows

def user_following(user):
    c = ContentType.objects.get_for_model(User)

    followers_qs = User.objects.filter(follow__object_id=user.pk, 
                                        follow__content_type=c).distinct()
    return followers_qs
User.following = user_following

def acstream_started_following_patch(sender, **kwargs):
    action = kwargs['instance']
    if action.verb == _('started following'):
        action.verb = 'started following'
signals.pre_save.connect(acstream_started_following_patch, sender=Action)
