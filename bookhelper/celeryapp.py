'''Starts celery for queued tasks
There is an extra (non-celery) command line argument '--sqlitedb='
to set both, broker and backend.
'''

import sys
from celery import Celery
import logging

dbpath = ""
for i, arg in enumerate(sys.argv):
    print (i, arg)
    if arg.startswith("--sqlitedb="):
        dbpath = arg.split("=")[-1]
        sys.argv.pop(i)
        break
print (__name__, dbpath)

celeryapp = Celery(
    'tasks',
    broker='sqla+sqlite:///%s' % dbpath,
    backend='db+sqlite:///%s' % dbpath)



@celeryapp.task
def async_action(action):
        action.run()
        logging.debug("ER + " + ",".join(action.errors))
        if action.errors:
            raise Exception(",".join(action.errors))


