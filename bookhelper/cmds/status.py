
'''versionizer.py

Creates new version of a book
'''
import os
import sys
from bookhelper import Book, doi
from bookhelper.celeryapp import celeryapp
from . import Action

class StatusAction(Action):
    def validate(self):
        if not self.conf.task_id:
                self.errors.append("Missing task id" )

    def run(self):
        result = celeryapp.AsyncResult(self.conf.task_id)
        #return result.state
        if result.state == "FAILURE":
            return str(result.get(timeout=1, propagate=False))
        return str(result.state)
