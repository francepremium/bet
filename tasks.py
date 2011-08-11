import time
import uwsgi

from django.core.management import call_command
from tasksconsumer import *

from gsm.management.commands.gsm_sync import Command as GsmSyncCommand

@queueconsumer('send_mail')
def send_mail(args={}):
    call_command('send_mail')
    call_command('retry_deferred')
    time.sleep(30)
    enqueue(queue='send_mail')

@queueconsumer('gsm_sync')
def gsm_sync(args={}):
    GsmSyncCommand().handle()
    call_command('update_index')
    time.sleep(30)
    enqueue(queue='gsm_sync')
