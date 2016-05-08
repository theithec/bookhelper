from os.path import  dirname, join
from celery import Celery

p = join(dirname(dirname(__file__)), "tmp")
import sys
#sys.exit(p)
celeryapp =  Celery(
    'tasks',
    broker='sqla+sqlite:///%s/celery.dbsqlite' % p,
    backend='db+sqlite:///%s/celery.dbsqlite' % p )


@celeryapp.task
def async_action(action):
        action.run()
