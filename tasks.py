import time
from yourlabs import runner

from django.core.management import call_command

from gsm.management.commands.gsm_sync import Command as GsmSyncCommand

def send_mail():
    call_command('send_mail')
    time.sleep(5*60)

def retry_deferred():
    call_command('retry_deferred')
    time.sleep(5*60)

def gsm_sync():
    GsmSyncCommand().handle(cooldown=3)
    time.sleep(20*60)

def gsm_sync_live():
    call_command('gsm_sync_live')
    time.sleep(7)

def update_index():
    call_command('update_index')
    time.sleep(5*60)
