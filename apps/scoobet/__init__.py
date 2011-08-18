from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

def prefetch_relations(weak_queryset):
    """
    Consider such a model class::

        class Action(models.Model):
            actor_content_type = models.ForeignKey(ContentType,related_name='actor')
            actor_object_id = models.PositiveIntegerField() 
            actor = generic.GenericForeignKey('actor_content_type','actor_object_id')
 
    And dataset::
        
        Action(actor=user1).save()
        Action(actor=user2).save()
    
    This will hit the user table once for each action::

        [a.actor for a in Action.objects.all()]

    Whereas this will hit the user table once::

        [a.actor for a in prefetch_relations(Action.objects.all())]

    Actually, the example above will hit the database N+1 times, where N is
    the number of actions. But with prefetch_relations(), the database will be
    hit N+1 times where N is the number of distinct content types.

    Here an example, making a list with prefetch_relations(), and then without prefetch_relations(). See the number of database hits after each test.
    
        In [1]: from django import db; from scoobet import *
        
        In [2]: db.reset_queries()
        
        In [3]: x = [(a.actor, a.action_object, a.target) for a in prefetch_relations(Action.objects.all().order_by('-pk'))]
        
        In [4]: print len(db.connection.queries)
        34
        
        In [5]: db.reset_queries()
        
        In [6]: print len(db.connection.queries)
        0
        
        In [7]: [x.actor for x in a]
        Display all 274 possibilities? (y or n)
        
        In [7]: x = [(a.actor, a.action_object, a.target) for a in Action.objects.all().order_by('-pk')]
        
        In [8]: print len(db.connection.queries)
        396
    """
    weak_queryset = weak_queryset.select_related()

    # reverse model's generic foreign keys into a dict:
    # { 'field_name': generic.GenericForeignKey instance, ... }
    gfks = {}
    for name, gfk in weak_queryset.model.__dict__.items():
        if not isinstance(gfk, generic.GenericForeignKey):
            continue
        gfks[name] = gfk

    data = {}
    for weak_model in weak_queryset:
        for gfk_name, gfk_field in gfks.items():
            related_content_type_id = getattr(weak_model, gfk_field.model._meta.get_field_by_name(gfk_field.ct_field)[0].get_attname())
            if not related_content_type_id:
                continue
            related_content_type = ContentType.objects.get_for_id(related_content_type_id)
            related_object_id = int(getattr(weak_model, gfk_field.fk_field))

            if related_content_type not in data.keys():
                data[related_content_type] = []
            data[related_content_type].append(related_object_id)

    for content_type, object_ids in data.items():
        model_class = content_type.model_class()
        models = prefetch_relations(model_class.objects.filter(pk__in=object_ids))
        for model in models:
            for weak_model in weak_queryset:
                for gfk_name, gfk_field in gfks.items():
                    related_content_type_id = getattr(weak_model, gfk_field.model._meta.get_field_by_name(gfk_field.ct_field)[0].get_attname())
                    if not related_content_type_id:
                        continue
                    related_content_type = ContentType.objects.get_for_id(related_content_type_id)
                    related_object_id = int(getattr(weak_model, gfk_field.fk_field))
                    
                    if related_object_id != model.pk:
                        continue
                    if related_content_type != content_type:
                        continue

                    setattr(weak_model, gfk_name, model)

    return weak_queryset
    
def group_activities(activities):
    if not activities:
        return activities

    #activities = prefetch_relations(activities)
    activities = activities

    previous = None
    group = []
    groups = []
    duplicates = []
    group_verbs = ('flagged', 'corrected')
    for activity in activities:
        # prevent duplicates
        if previous and activity.verb == previous.verb and activity.verb not in group_verbs and activity.actor == previous.actor and activity.target == previous.target and activity.action_object == previous.action_object:
            # just ignore duplicates, ie. if user click follow/unfollow a lot
            activity.hide = True

        if previous and activity.verb == previous.verb and activity.verb in group_verbs and activity.actor == previous.actor:
            do_group = True
        else:
            do_group = False

        if do_group:
            # this activity groups with the previous one
            group.append(activity)
        else:
            # this activity does not group with the previous one
            # save the previous group if there is a previous one
            if previous:
                groups.append(group)
            # create a new group
            group = [activity]

        # the activity may need to know its own group
        activity.group = group

        # this activity is the "previous" one of the next loop
        previous = activity

    # if the last activity groupped then it would not have been appended to groups
    if len(groups) < 1 or groups[-1] is not group:
        groups.append(group)

    # second pass, adding properties to activities, required to display
    for group in groups:
        # the first of each group opens the activity line
        group[0].open = True
        # the last of each group closes the activity line
        group[-1].close = True
        if getattr(group[0], 'action_object', False):
            # action objects must be grouped in their own list for render_tracks and such
            action_object_group = [a.action_object for a in group]
            # and given to the closer
            group[-1].action_object_group = action_object_group
        # the earliest activity of the group is the one to comment
        earliest = None
        for activity in group:
            if earliest is None:
                earliest = activity
            elif earliest.pk > activity.pk:
                earliest = activity
        for activity in group:
            activity.earliest_of_group = earliest

    activities[0].open = True
    activities[len(activities)-1].close = True

    return activities
