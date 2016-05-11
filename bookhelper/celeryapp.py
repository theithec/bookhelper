from os.path import dirname, join
from celery import Celery
import logging

p = join(dirname(dirname(__file__)), "tmp")
celeryapp = Celery(
    'tasks',
    broker='sqla+sqlite:///%s/celery.dbsqlite' % p,
    backend='db+sqlite:///%s/celery.dbsqlite' % p)


@celeryapp.task
def async_action(action):
        action.run()
        logging.debug("ER + " + ",".join(action.errors))
        if action.errors:
            raise Exception(",".join(action.errors))
        #return self.action.errors
