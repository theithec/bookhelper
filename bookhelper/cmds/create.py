'''
Creates a boook from json-data.

Eample:
python -m bookhelper -c bookhelper.cfg create \
'{"title": "Book1",  "pages": [{"title": "Book1", "body": "Text1"}, \
{"title": "Einleitung", "toctitle": "zur Eil", "body": "BAla"}], \
"info": {"AUTOREN": "x"}}'

If the title of a page is the booktitle, then the body will be included in the
generated startpage.
'''

import os
import json
import logging
from . import SiteAction
from bookhelper.utils import template_from_info, on_no_errors


class CreateAction(SiteAction):

    def validate(self):
        jsrc = getattr(self.conf, "json_source", None)
        if not jsrc:
            self.errors.append("No json source")
            return

        try:
            self.bookdata = json.loads(jsrc)
        #  except json.decoder.JSONDecodeError as e:
        except ValueError as e:
            self.errors.append(str(e))
            return
        for key in ('title', 'info', 'pages'):
            v = self.bookdata.get(key, None)
            if not v:
                self.errors.append("Missing key: %s" % key)

    @on_no_errors
    def save_page(self, title, content):
        logging.debug("Try save page: %s" % title)
        logging.debug("conf: %s" % self.conf.__dict__)
        page = self.site.Pages[title]

        if page.text() and not self.conf.force_overwrite:
            self.errors.append("Page already exists: %s" % title)
            return
        page.save(content)
        return page

    def mk_page(self, page):
        txt = "\n%s\n" % page['body']
        self.save_page(os.path.join(self.title, page['title']), txt)

    def mk_toc(self):
        toc = '\n==Inhaltsverzeichnis==\n'
        toc += '\n<div class="BookTOC">\n'
        for page in self.pages:
            title = page['title']
            toctitle = page.get('toctitle', title)
            toc += "\n# [[%s|%s]]\n" % (
                os.path.join(self.title, title),
                toctitle)
        toc += "\n</div>\n"
        return toc

    def mk_book_page(self):
        txt = ''
        tmpl = template_from_info(self.bookdata['info'])
        if tmpl:
            txt += tmpl
        else:
            self.errors.append("No valid info found")
            return
        titlepagelist = [
            p for p in self.pages
            if self.title == p['title']]
        if titlepagelist:
            titlepage = titlepagelist[0]
            txt += "\n %s \n " % titlepage['body']
            self.pages.pop(self.pages.index(titlepage))

        txt += "\n%s" % self.mk_toc()
        txt += "\n[[Kategorie:Buch]]"
        return self.save_page(self.title, txt)

    @on_no_errors
    def create(self):
        self.title = self.bookdata['title']
        self.pages = self.bookdata['pages']
        self.book_page = self.mk_book_page()
        for page in self.pages:
            self.mk_page(page)

    @on_no_errors
    def run(self):
        self.validate()
        self.create()


