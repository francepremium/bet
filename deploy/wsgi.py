# pinax.wsgi is configured to live in projects/main/deploy.

import os
import sys

from os.path import abspath, dirname, join
from site import addsitedir

sys.path.insert(0, abspath(join(dirname(__file__), "../../")))

from django.conf import settings
os.environ["DJANGO_SETTINGS_MODULE"] = "settings"

sys.path.insert(0, join(settings.PROJECT_ROOT, "apps"))

from tasksconsumer import enqueue
enqueue(queue='gsm_sync')

from django.core.handlers.wsgi import WSGIHandler
#class application(WSGIHandler):
    #def __call__(self, environ, start_response):
        #return super(application, self).__call__(environ, start_response)
application = WSGIHandler()
