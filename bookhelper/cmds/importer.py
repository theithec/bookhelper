import os
import os.path
import yaml
import json
import pypandoc
from . import Action
from .create import CreateAction


class ImportAction(Action):
    '''Makes a book from files in conf.sourcepath (if valid)'''

    def validate(self):
        spath = getattr(self.conf, 'source_path', None)
        if spath.endswith('/'):
            spath = spath[:-1]
            if not spath:
                self.errors.append("No sourcecpath given")

            elif not os.path.isdir(spath):
                self.errors.append("%s is not a directory" % spath)

            elif not os.path.isfile(os.path.join(spath, 'title.txt')):
                self.errors.append("%s not found" % (os.path.join(spath, 'title.txt')))

        self.source_path = spath

    def mk_pages(self):
        self.pagesdata = []
        for fname in self.files:
            if not (fname.endswith(".md" or fname.endswith(".markdown"))):
                continue
            with open(os.path.join(self.source_path, fname)) as f:
                md = f.read()
                body = pypandoc.convert(md, "mediawiki", format="md")
                title =  fname.split("-", maxsplit=1)[-1] # rm "01-" ...
                title = title.rsplit(".", maxsplit=1)[0] # rm filetype
                p = {
                    'title': title,
                    'body': body
                }
                self.pagesdata.append(p)

    def mk_info(self):
        with open(os.path.join(self.source_path, 'title.txt')) as f:
            data = (yaml.safe_load(f))
            self.infodata = dict([(k.upper(), v) for k,v in data.items()])

    def create(self):
        self.conf.json_source = json.dumps({
            'title': self.title,
            'pages': self.pagesdata,
            'info': self.infodata
        })

        ca = CreateAction(self.conf)
        ca.validate()
        ca.run()
        self.errors += ca.errors

    def run(self):
        files =  os.listdir(self.source_path)
        files.pop(files.index('title.txt'))
        self.files = sorted(files)
        print("files", files)
        self.title = os.path.basename(os.path.abspath(self.source_path))
        self.mk_pages()
        self.mk_info()
        self.create()
        '''jdata = {
            'title': title,
            'pages': self.mk_pages(),
            'info': self.mk_info()
        }'''
