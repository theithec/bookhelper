from bookhelper import on_no_errors
from bookhelper.cmds import publish, versionize, status, create, importer


class Starter(object):

    command_mapping = {
        "publish": publish.PublishAction,
        "versionize": versionize.VersionizeAction,
        "status": status.StatusAction,
        "create": create.CreateAction,
        "import": importer.ImportAction,
    }

    def __init__(self, conf):
        self.errors = []
        self.conf = conf
        self.action = self.get_action()

    def start(self):
        self.action.validate()
        self.errors += self.action.errors
        res = "FAILED"
        if not self.errors:
            res = self.run_cmd()
        if not self.errors:
            if not res:
                res = "SUCCESS"
        return res

    @on_no_errors
    def get_action(self):
        Action = self.command_mapping[self.conf.cmd]
        return Action(self.conf)

    def run_cmd(self):
        if self.conf.queued:
            # ugly, but ...
            # celeryapp expects "--sqlitedb" in  sys.argv
            import sys
            sys.argv.append('--db-path=%s' % (self.conf.tmp_path))
            #sys.exit(str(sys.argv))
            from bookhelper.celeryapp import async_action
            task = async_action.delay(self.action)
            return task.id
        else:
            res = self.action.run()
            self.errors += self.action.errors
            return res

