from django.core.management import call_command
from tasksconsumer import *
import uwsgi

@queueconsumer('gsm_sync')
def gsm_sync(args):
    call_command('gsm_sync')
    call_command('update_index')
    return uwsgi.SPOOL_RETRY
