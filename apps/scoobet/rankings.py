from django.contrib.auth.models import User
from django.utils.datastructures import SortedDict

from gsm.models import *

def rankings_for_sport(sport):
    select_won_bet_count = '''
select 
    count(b.id) 
from 
    bet_bet b
left join
    bet_ticket t on t.id = b.ticket_id
left join
    gsm_session s on s.id = b.session_id
where
    correction = 1 
    and t.user_id = auth_user.id
    and s.sport_id = %s
'''
    select_bet_count = '''
select 
    count(b.id) 
from 
    bet_bet b
left join
    bet_ticket t on t.id = b.ticket_id
left join
    gsm_session s on s.id = b.session_id
where
    t.user_id = auth_user.id
    and s.sport_id = %s
'''
    select_average_odds = '''
select 
    avg(b.odds) 
from 
    bet_bet b
left join
    bet_ticket t on t.id = b.ticket_id
left join
    gsm_session s on s.id = b.session_id
where
    t.user_id = auth_user.id
    and s.sport_id = %s
'''
    qs = User.objects.filter(ticket__bet__session__sport=sport).extra(
        select = SortedDict([
            ('won_bet_count', select_won_bet_count),
            ('bet_count', select_bet_count),
            ('average_odds', select_average_odds),
        ]),
        select_params = (str(sport.pk), str(sport.pk), str(sport.pk),)
    ).distinct().order_by('-won_bet_count')
    
    return qs
Sport.get_rankings = rankings_for_sport

def rankings_for_competition(competition):
    select_won_bet_count = '''
select 
    count(b.id) 
from 
    bet_bet b
left join
    bet_ticket t on t.id = b.ticket_id
left join
    gsm_session s on s.id = b.session_id
left join
    gsm_season ss on s.season_id = ss.id
where
    correction = 1 
    and t.user_id = auth_user.id
    and ss.competition_id = %s
'''
    select_bet_count = '''
select 
    count(b.id) 
from 
    bet_bet b
left join
    bet_ticket t on t.id = b.ticket_id
left join
    gsm_session s on s.id = b.session_id
left join
    gsm_season ss on s.season_id = ss.id
where
    t.user_id = auth_user.id
    and ss.competition_id = %s
'''
    select_average_odds = '''
select 
    avg(b.odds) 
from 
    bet_bet b
left join
    bet_ticket t on t.id = b.ticket_id
left join
    gsm_session s on s.id = b.session_id
left join
    gsm_season ss on s.season_id = ss.id
where
    t.user_id = auth_user.id
    and ss.competition_id = %s
'''
    qs = User.objects.filter(ticket__bet__session__season__competition=competition).extra(
        select = SortedDict([
            ('won_bet_count', select_won_bet_count),
            ('bet_count', select_bet_count),
            ('average_odds', select_average_odds),
        ]),
        select_params = (str(competition.pk), str(competition.pk), str(competition.pk),)
    ).distinct().order_by('-won_bet_count')
    
    return qs
Competition.get_rankings = rankings_for_competition

def rankings_for_team(team):
    select_won_bet_count = '''
select 
    count(b.id) 
from 
    bet_bet b
left join
    bet_ticket t on t.id = b.ticket_id
left join
    gsm_session s on s.id = b.session_id
where
    correction = 1 
    and t.user_id = auth_user.id
    and (s."oponnent_A_id" = %s or s."oponnent_B_id" = %s)
'''
    select_bet_count = '''
select 
    count(b.id) 
from 
    bet_bet b
left join
    bet_ticket t on t.id = b.ticket_id
left join
    gsm_session s on s.id = b.session_id
where
    t.user_id = auth_user.id
    and (s."oponnent_A_id" = %s or s."oponnent_B_id" = %s)
'''
    select_average_odds = '''
select 
    avg(b.odds) 
from 
    bet_bet b
left join
    bet_ticket t on t.id = b.ticket_id
left join
    gsm_session s on s.id = b.session_id
where
    t.user_id = auth_user.id
    and (s."oponnent_A_id" = %s or s."oponnent_B_id" = %s)
'''
    qs = User.objects.filter(
        Q(ticket__bet__session__oponnent_A=team)|
        Q(ticket__bet__session__oponnent_B=team)).extra(
            select = SortedDict([
                ('won_bet_count', select_won_bet_count),
                ('bet_count', select_bet_count),
                ('average_odds', select_average_odds),
            ]),
            select_params = (str(team.pk), str(team.pk), str(team.pk), 
                             str(team.pk), str(team.pk), str(team.pk),)
    ).distinct().order_by('-won_bet_count')
    
    return qs
GsmEntity.get_rankings = rankings_for_team
