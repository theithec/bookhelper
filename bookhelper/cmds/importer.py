'''
Imports a book from files in a directory (the source_path)
Expects the following structure:
    title.txt with yaml metadata
    01-somename.md (or .markdown)
    02-someothername.md (or .markdown)

Note that everything left of and including the first occurance of "-" will be
removed from the filename.
For now the title of the book is the name of the directory.

'''
import os
import os.path
import yaml
import json
import pypandoc
from jinja2 import Environment, FileSystemLoader
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
                self.errors.append(
                    "%s not found" % (os.path.join(spath, 'title.txt')))

        self.source_path = spath

    def mk_pages(self):
        env = Environment(loader=FileSystemLoader(searchpath=self.source_path))
        templatenames = sorted(env.list_templates("md"))
        vars_dict = {}
        try:
            with open(os.path.join(self.source_path, "vars.json")) as vars_json:
                vars_dict = json.load(vars_json)
        except Exception as e:
            import sys
            sys.exit(e)
            pass

        self.pagesdata = []
        for templatename in templatenames:
            template = env.get_template(templatename)
            md = template.render(vars_dict)
            body = pypandoc.convert(md, "mediawiki", format="md")
            title = templatename.split("-", maxsplit=1)[-1]  # rm "01-" ...
            title = title.rsplit(".", maxsplit=1)[0]  # rm filetype
            p = {
                'title': title,
                'body': body
            }
            self.pagesdata.append(p)

    def mk_info(self):
        with open(os.path.join(self.source_path, 'title.txt')) as f:
            self.infodata = yaml.safe_load(f)

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
        self.title = os.path.basename(os.path.abspath(self.source_path))
        self.mk_pages()
        self.mk_info()
        self.create()
