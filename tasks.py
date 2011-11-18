from datetime import timedelta as td
import time
from yourlabs import runner

from django.core.management import call_command

from gsm.management.commands.gsm_sync_new import Command as GsmSyncNewCommand

@runner.task(
    success_cooldown=td(minutes=5), 
    fail_cooldown=td(minutes=5),
    non_recoverable_downtime=td(hours=24))
def send_mail():
    call_command('send_mail')

@runner.task(
    success_cooldown=td(minutes=5), 
    fail_cooldown=td(minutes=5),
    non_recoverable_downtime=td(hours=24))
def retry_deferred():
    call_command('retry_deferred')

@runner.task(
    success_cooldown=td(seconds=4),
    fail_cooldown=td(minutes=2),
    non_recoverable_downtime=td(hours=3))
def gsm_sync():
    call_command('gsm_sync_new', noreload=True)
