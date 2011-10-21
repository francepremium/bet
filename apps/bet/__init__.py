from django.db.models import get_model

import gsm

TICKET_STATUS_INCOMPLETE = 0
TICKET_STATUS_DONE = 1

BET_CORRECTION_NEW = 0
BET_CORRECTION_WON = 1
BET_CORRECTION_CANCELED = 2
BET_CORRECTION_LOST = 3

EVENT_KIND_CORRECTION = 1
EVENT_KIND_FLAG = 2

def correct_for_session(session, element=None):
    if element is None:
        tree = gsm.get_tree('en', session.sport, 'get_matches', retry=30,
            type='match', id=session.gsm_id)
        
        for element in gsm.parse_element_for(tree.getroot(), 'match'):
            break

    from bet.models import *
    User = get_model('auth', 'user')
    BetType = get_model('bookmaker', 'bettype')

    if element.attrib['status'] in ('Fixture', 'Playing'):
        return
    
    if element.attrib['status'] == 'Cancelled':
        Bet.objects.filter(session=session).update(correction=BET_CORRECTION_CANCELED)
        return

    rewrite = (
        'fs_A',
        'fs_B',
        'hts_A',
        'hts_B',
        'ets_A',
        'ets_B',
    )

    attrib = {}
    for k, v in element.attrib.items():
        if v.isdigit():
            attrib[k] = float(v)
        else:
            attrib[k] = v

    to_update = User.objects.filter(ticket__bet__session=session).distinct()
    to_correct = BetType.objects.filter(bet__session=session).distinct()
    print to_correct, [t.pk for t in to_correct]
    for t in to_correct:
        for c in t.betchoice_set.all():
            bets = Bet.objects.filter(session=session, bettype=t, choice=c)

            try:
                condition = c.condition
                if condition is None:
                    raise
                for var in rewrite:
                    condition = condition.replace(var, 'attrib["%s"]' % var)
                
                set = []
                for child in element.getchildren():
                    if child.tag == 'set':
                        set.append(element.attrib)

                result = eval(condition)
                if result:
                    correction = BET_CORRECTION_WON
                else:
                    correction = BET_CORRECTION_LOST

                bets.update(correction=correction)
            except:
                bets.update(flagged=True)

    for u in to_update.values_list('pk', flat=True):
        print 'refreshing', u
        refresh_betprofile_for_user({'userpk': u})
