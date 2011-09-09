import logging

from django.core.management.base import BaseCommand, CommandError

from gsm.management.commands.gsm_sync import Command as GsmSyncCommand
from yourlabs import runner

logger = logging.getLogger('gsm_runner')

class Command(BaseCommand):
    args = 'n/a'
    help = 'Run gsm_sync and update_index continuously'

    def handle(self, *args, **kwargs):
        def gsm_sync():
            GsmSyncCommand().handle(cooldown=3)
        def update_index():
            call_command('update_index')
        
        r = runner.Runner([gsm_sync, update_index], logger)
        r.run()
