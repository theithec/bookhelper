'''status.py

Gets the state of a celery task by id
'''
from . import Action


class StatusAction(Action):

    def init(self):
        if not self.conf.task_id:
                self.errors.append("Missing task id")

    def run(self):
        from bookhelper.celeryapp import celeryapp
        result = celeryapp.AsyncResult(self.conf.task_id)
        if result.state == "FAILURE":
            return str(result.get(timeout=1, propagate=False))
        return str(result.state)
