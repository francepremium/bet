def group_activities(activities):
    if not activities:
        return activities

    previous = None
    group = []
    groups = []
    group_verbs = ('flagged', 'corrected')
    for activity in activities:
        if previous and activity.verb == previous.verb and activity.verb in group_verbs and activity.actor == previous.actor:
            if activity.verb == 'added track to playlist' and activity.target != previous.target:
                do_group = False
            else:
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


