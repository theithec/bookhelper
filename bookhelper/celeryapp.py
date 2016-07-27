
'''Starts celery for queued tasks
There is an extra (non-celery) command line argument '--db-path='
to set both, broker and backend.
'''

import sys
from celery import Celery
import logging


dbpath = ""
for i, arg in enumerate(sys.argv):
    if arg.startswith("--db-path="):
        dbpath = arg.split("=")[-1]
        sys.argv.pop(i)
        break

if not dbpath.endswith("/"):
    dbpath += "/"

dbpath += "celery.sqlitedb"

celeryapp = Celery(
    'tasks',
    broker='sqla+sqlite:///%s' % dbpath,
    backend='db+sqlite:///%s' % dbpath)


@celeryapp.task
def async_action(Action, conf):
        action = Action(conf)
        logging.debug("ER + " + ",".join(action.errors))
        if action.errors:
            raise Exception(",".join(action.errors))


