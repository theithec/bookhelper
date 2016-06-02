u'''
Imports a book from files in a directory (the source_path)
Expects the following structure:
    title.txt with yaml metadata
    01-somename.md (or .markdown)
    02-someothername.md (or .markdown)

Note that everything left of and including the first occurance of "-" will be
removed from the filename.
For now the title of the book is the name of the directory.

'''
from __future__ import with_statement
from __future__ import absolute_import
import os
import os.path
import yaml
import json
import pypandoc
from . import Action
from .create import CreateAction
from io import open


class ImportAction(Action):
    u'''Makes a book from files in conf.sourcepath (if valid)'''

    def validate(self):
        spath = getattr(self.conf, u'source_path', None)
        if spath.endswith(u'/'):
            spath = spath[:-1]
            if not spath:
                self.errors.append(u"No sourcecpath given")

            elif not os.path.isdir(spath):
                self.errors.append(u"%s is not a directory" % spath)

            elif not os.path.isfile(os.path.join(spath, u'title.txt')):
                self.errors.append(
                    u"%s not found" % (os.path.join(spath, u'title.txt')))

        self.source_path = spath

    def mk_pages(self):
        self.pagesdata = []
        for fname in self.files:
            if not (fname.endswith(u".md" or fname.endswith(u".markdown"))):
                continue
            with open(os.path.join(self.source_path, fname)) as f:
                md = f.read()
                body = pypandoc.convert(md, u"mediawiki", format=u"md")
                title = fname.split(u"-", maxsplit=1)[-1]  # rm "01-" ...
                title = title.rsplit(u".", maxsplit=1)[0]  # rm filetype
                p = {
                    u'title': title,
                    u'body': body
                }
                self.pagesdata.append(p)

    def mk_info(self):
        with open(os.path.join(self.source_path, u'title.txt')) as f:
            self.infodata = yaml.safe_load(f)

    def create(self):
        self.conf.json_source = json.dumps({
            u'title': self.title,
            u'pages': self.pagesdata,
            u'info': self.infodata
        })

        ca = CreateAction(self.conf)
        ca.validate()
        ca.run()
        self.errors += ca.errors

    def run(self):
        files = os.listdir(self.source_path)
        files.pop(files.index(u'title.txt'))
        self.files = sorted(files)
        self.title = os.path.basename(os.path.abspath(self.source_path))
        self.mk_pages()
        self.mk_info()
        self.create()
