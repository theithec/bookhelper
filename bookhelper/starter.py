from bookhelper.cmds import (
    publish, status, versionize, create, setup) # , importer, setup)


class Starter(object):

    command_mapping = {
        "publish": publish.PublishAction,
        "versionize": versionize.VersionizeAction,
        "status": status.StatusAction,
        "create": create.CreateAction,
        # "import": importer.ImportAction,
        "setup": setup.SetupAction,
    }

    def __init__(self, conf):
        self.errors = []
        self.conf = conf
        #        self.action = self.get_action()

    def start(self):
        res = self.run_cmd()
        if not res:
            res = "SUCCESS" if not self.errors else "FAILURE"
        return res


    def run_cmd(self):
        Action = self.command_mapping[self.conf.cmd]
        import sys
        sys.argv.append('--db-path=%s' % (self.conf.tmp_path))
        if self.conf.queued:
            from bookhelper.celeryapp import async_action
            task = async_action.delay(Action, self.conf)
            return task.id
        else:
            action = Action(self.conf)
            self.errors += action.errors
            return action.result

