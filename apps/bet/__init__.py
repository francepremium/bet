from celery.task import task

from models import *

@task(ignore_result=True)
def foo():
    pass
