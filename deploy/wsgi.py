# pinax.wsgi is configured to live in projects/main/deploy.

import os
import sys

from os.path import abspath, dirname, join
from site import addsitedir

sys.path.insert(0, abspath(join(dirname(__file__), "../../")))

from django.conf import settings
os.environ["DJANGO_SETTINGS_MODULE"] = "settings"

sys.path.insert(0, join(settings.PROJECT_ROOT, "apps"))

from django.core.handlers.wsgi import WSGIHandler
application = WSGIHandler()

#wait until upstream stabilizes it
#from tasksconsumer import enqueue
#enqueue(queue='gsm_sync')
#enqueue(queue='send_mail')
