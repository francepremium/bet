import time.sleep()
from yourlabs import runner

from django.core.management import call_command

from gsm.management.commands.gsm_sync import Command as GsmSyncCommand

def send_mail():
    call_command('send_mail')
    time.sleep(3*60)

def retry_deferred():
    call_command('retry_deferred')
    time.sleep(3*60)

def gsm_sync():
    GsmSyncCommand().handle(cooldown=3)
    time.sleep(3*60)

def gsm_sync_live():
    call_command('gsm_sync_live')
    time.sleep(5)

def update_index():
    call_command('update_index')
    time.sleep(3*60)
