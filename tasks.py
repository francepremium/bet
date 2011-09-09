import logging
import time
import uwsgi

from django.core.management import call_command
from tasksconsumer import *

from gsm.management.commands.gsm_sync import Command as GsmSyncCommand

logger = logging.getLogger('gsm')

logger.info('imported')

@queueconsumer('gsm_sync')
def gsm_sync(args={}):
    logger.info('started gsm_sync function')
    return uwsgi.SPOOL_RETRY
    cooldowns = (1,2,3,4)
    attempt = 0
    while attempt <= len(cooldowns):
        e = None
        try:
            logger.info('started gsm_sync actual task')
            raise Exception()
        except Exception as e:
            logger.info("Caught %s while doing gsm_sync for the %s th time, sleep %s seconds and retry" % (e, attempt, cooldowns[attempt]))
            time.sleep(cooldowns[attempt])
            attempt += 1

    if e is not None:
        logger.error('Failed %s times' % len(cooldowns))
        # notify admins...

    enqueue(queue='gsm_sync')
    logger.info('enqueued self again')


    # old code
    #GsmSyncCommand().handle(cooldown=3)
    #call_command('update_index')
    #time.sleep(30)

