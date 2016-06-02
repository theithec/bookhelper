u'''Starts celery for queued tasks
There is an extra (non-celery) command line argument '--db-path='
to set both, broker and backend.
'''

from __future__ import absolute_import
import sys
from celery import Celery
import logging


dbpath = u""
for i, arg in enumerate(sys.argv):
    if arg.startswith(u"--db-path="):
        dbpath = arg.split(u"=")[-1]
        sys.argv.pop(i)
        break

if not dbpath.endswith(u"/"):
    dbpath += u"/"

dbpath += u"celery.sqlitedb"

celeryapp = Celery(
    u'tasks',
    broker=u'sqla+sqlite:///%s' % dbpath,
    backend=u'db+sqlite:///%s' % dbpath)


@celeryapp.task
def async_action(action):
        action.run()
        logging.debug(u"ER + " + u",".join(action.errors))
        if action.errors:
            raise Exception(u",".join(action.errors))


