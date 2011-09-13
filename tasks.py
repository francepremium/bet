from datetime import timedelta as td
import time
from yourlabs import runner

from django.core.management import call_command

from gsm.management.commands.gsm_sync import Command as GsmSyncCommand

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
    success_cooldown=td(hours=3), 
    fail_cooldown=td(minutes=15),
    non_recoverable_downtime=td(hours=24))
def gsm_sync():
    GsmSyncCommand().handle(cooldown=3)

@runner.task(
    success_cooldown=td(seconds=20), 
    fail_cooldown=td(minutes=1),
    non_recoverable_downtime=td(hours=12))
def gsm_sync_live():
    call_command('gsm_sync_live')
    time.sleep(7)

@runner.task(
    success_cooldown=td(minutes=5), 
    fail_cooldown=td(minutes=15),
    non_recoverable_downtime=td(hours=24))
def update_index():
    call_command('update_index')
    time.sleep(5*60)
