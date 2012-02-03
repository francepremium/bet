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
            type=session.tag, id=session.gsm_id, detailed=True)
        
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
        'p1s_A',
        'p1s_B',
        'p2s_A',
        'p2s_B',
        'p3s_A',
        'p3s_B',
        'p4s_A',
        'p4s_B',
        'ps_A',
        'ps_B',
        'eps_A',
        'eps_B',
    )

    attrib = {}
    for k, v in element.attrib.items():
        if v.isdigit():
            attrib[k] = float(v)
        else:
            attrib[k] = v

    to_update = User.objects.filter(ticket__bet__session=session).distinct()
    to_correct = BetType.objects.filter(bet__session=session, variable_type=None).distinct()

    for t in to_correct:
        if t.cancel_condition:
            try:
                condition = t.cancel_condition
                if condition is None:
                    raise
                for var in rewrite:
                    condition = condition.replace(var, 'attrib["%s"]' % var)
                result = eval(condition)
                if result:
                     Bet.objects.filter(session=session, bettype=t).update(
                        correction=BET_CORRECTION_CANCELED)
                     continue
            except:
                pass

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
        refresh_betprofile_for_user_nospool({'userpk': u})
    
    # the next part uses bet.save() which should trigger profile refresh

    to_correct = Bet.objects.filter(session=session).exclude(bettype__variable_type=None
        ).distinct()

    goalers = []
    goalers_with_extra = []
    goal_elements = element.findall('goals/goal/event') or []
    for e in goal_elements:
        if e.attrib['code'] != 'G':
            pass

        if not e.attrib.get('minute_extra', None):
            goalers.append(float(e.attrib['person_id']))

        goalers_with_extra.append(float(e.attrib['person_id']))

    for bet in to_correct:
        try:
            condition = bet.choice.condition
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
            bet.correction = correction
        except:
            bet.flagged = True
        bet.save()

class BetTooLateException(Exception):
    def __init__(self, bet):
        self.bet = bet
