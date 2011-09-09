from django.core.management import call_command

from gsm.management.commands.gsm_sync import Command as GsmSyncCommand

def send_mail(args={}):
    call_command('send_mail')

def retry_deferred():
    call_command('retry_deferred')

def gsm_sync():
    GsmSyncCommand().handle(cooldown=3)

def update_index():
    call_command('update_index')
