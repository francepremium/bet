from django.db.models import signals
from django.db import models
from django.contrib.contenttypes.models import ContentType

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
    if not kwargs['instance'].user:
        return None
    action.send(kwargs['instance'].user, verb='commented',
        action_object=kwargs['instance'].content_object)
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
