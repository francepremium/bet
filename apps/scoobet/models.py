from django.db.models import signals
from django.db import models

from actstream import action

def user_registered_activity(sender, **kwargs):
    if not kwargs.get('created', False):
        return None
    action.send(kwargs['instance'], verb='registered')
signals.post_save.connect(user_registered_activity, 
    sender=models.get_model('auth', 'user'))
