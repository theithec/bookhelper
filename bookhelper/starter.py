from __future__ import absolute_import
from bookhelper import on_no_errors
from bookhelper.cmds import publish, versionizer, status
from bookhelper.celery import async_action


class Starter(object):

    command_mapping = {
        u"publish": publish.PublishAction,
        u"versionize": versionizer.VersionizeAction,
        u"status": status.StatusAction
    }

    def __init__(self, conf):
        self.errors = []
        self.conf = conf
        self.action = self.get_action()

    def start(self):
        self.action.validate()
        self.errors += self.action.errors
        #print("ERR1", self.errors)
        #import sys; sys.exit()
        if not self.errors:

            return self.run_cmd()
        else:
            return u"FAILED"

    @on_no_errors
    def get_action(self):
        Action = self.command_mapping[self.conf.cmd]
        return Action(self.conf)

    def run_cmd(self):
        if self.conf.queued:
            task = async_action.delay(self.action)
            return task.id
        else:
            res = self.action.run()
            self.errors += self.action.errors
            return res
