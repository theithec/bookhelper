
'''status.py

Gets the state of a celery task by id
'''
import os
import sys
from bookhelper import Book, doi
from . import Action

class StatusAction(Action):
    def validate(self):
        if not self.conf.task_id:
                self.errors.append("Missing task id" )

    def run(self):
        from bookhelper.celeryapp import celeryapp
        result = celeryapp.AsyncResult(self.conf.task_id)
        #return result.state
        if result.state == "FAILURE":
            return str(result.get(timeout=1, propagate=False))
        return str(result.state)
