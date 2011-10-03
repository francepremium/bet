from subscription.examples.yourlabs.apps import comments
comments.signals.comment_was_posted.connect(comments.comments_subscription)
comments.signals.comment_was_posted.connect(
    comments.comment_lazy_template_notification)

from subscription.examples.yourlabs.apps import auth
auth.signals.post_save.connect(auth.subscribe_user_to_himself, sender=auth.User)
auth.signals.post_syncdb.connect(auth.subscribe_existing_users_to_themselves)

from subscription.examples.yourlabs.apps import actstream
actstream.signals.post_save.connect(actstream.subscribe_user_to_his_action, 
    sender=actstream.Action)
actstream.signals.post_save.connect(actstream.follow_lazy_template_notification,
    sender=actstream.Follow)

from subscription.examples.yourlabs.apps import django_messages
django_messages.signals.post_save.connect(django_messages.message_notification,
    sender=django_messages.Message)
