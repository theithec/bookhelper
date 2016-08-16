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
        # import pdb; pdb.set_trace()
        self.errors = []
        if result.state == "FAILURE":
            try:
                str(result.get(timeout=1, propagate=True))
            except Exception as e:
                self.errors.append(str(e))
        self.result = result.state
        # return str(result.state)
