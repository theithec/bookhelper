import sys

from bookhelper import on_no_errors
from bookhelper.cmds import publish, versionizer, status
from bookhelper.celery import async_action

class Starter(object):

    command_mapping = {
        "publish": publish.PublishAction,
        "versionize": versionizer.VersionizeAction,
        "status": status.StatusAction
    }

    def __init__(self, conf):
        self.errors = []
        self.conf = conf
        self.action = self.get_action()

    def start(self):
        self.action.validate()
        self.errors += self.action.errors
        if not self.errors:
            return self.run_cmd()
        else:
            return "FAILED"

    @on_no_errors
    def get_action(self):
        Action = self.command_mapping[self.conf.cmd]
        return Action(self.conf)

    def run_cmd(self):
        #import pdb; pdb.set_trace()
        if self.conf.queued:
            #try:
            #    task = start_asynchron.delay(Starter, args)
            #    result = task.id
            #except Exception as e:
            #    errors.append("CELERY_ERR " + str(e))
            #    logging.debug("Celery task : %s" % task)
            task = async_action.delay(self.action)
            return task.id
        else:
            return self.action.run()

