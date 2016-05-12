import os.path
from . import Action


class ImportAction(Action):
    '''Makes a book from files in conf.sourcepath (if valid)'''

    def validate(self):
        print("C", self.conf)
        spath = getattr(self.conf, 'source_path', None)
        if not spath:
            self.errors.append("No sourcecpath given")

        elif not os.path.isdir(spath):
           self.errors.append("%s is not a directory" % spath)

        elif not os.path.isfile(os.path.join(spath, 'toc.md')):
            self.errors.append("%s not found" % (os.path.join(spath, 'toc.md')))



    def run(self):
        pass

