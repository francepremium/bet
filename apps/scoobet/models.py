from django.db.models import signals, Q
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User

from actstream import action
from actstream.models import Action, Follow

def user_registered_activity(sender, **kwargs):
    if not kwargs.get('created', False):
        return None
    action.send(kwargs['instance'], verb='registered')
signals.post_save.connect(user_registered_activity, 
    sender=models.get_model('auth', 'user'))

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

def comment_posted_activity(sender, **kwargs):
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
signals.post_save.connect(comment_posted_activity, sender=models.get_model('comments', 'Comment'))

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
    )
    return target_choices_qs
User.friends = user_friends

def user_follows(user):
    c = ContentType.objects.get_for_model(User)

    follows_users_ids = Follow.objects.filter(user=user,
                                              content_type__app_label='auth',
                                              content_type__model='user') \
                                      .exclude(object_id=user.pk) \
                                      .values_list('object_id', flat=True)
    return User.objects.filter(pk__in=follows_users_ids)
User.follows = user_follows

def user_following(user):
    c = ContentType.objects.get_for_model(User)

    followers_qs = User.objects.filter(follow__object_id=user.pk, 
                                        follow__content_type=c)
    return followers_qs
User.following = user_following
