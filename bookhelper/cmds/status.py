
u'''versionizer.py

Creates new version of a book
'''
from __future__ import absolute_import
import os
import sys
from bookhelper import Book, doi
from bookhelper.celery import celeryapp
from . import Action

class StatusAction(Action):
    def validate(self):
        if not self.conf.task_id:
                self.errors.append(u"Missing task id" )

    def run(self):
        return unicode(celeryapp.AsyncResult(self.conf.task_id).state)
