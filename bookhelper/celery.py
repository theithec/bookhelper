from __future__ import absolute_import
from os.path import dirname, join
from celery import Celery

p = join(dirname(dirname(__file__)), u"tmp")
celeryapp = Celery(
    u'tasks',
    broker=u'sqla+sqlite:///%s/celery.dbsqlite' % p,
    backend=u'db+sqlite:///%s/celery.dbsqlite' % p)


@celeryapp.task
def async_action(action):
        action.run()
