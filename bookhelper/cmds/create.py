u'''
Creates a boook from json-data.

Eample:
python -m bookhelper -c bookhelper.cfg create \
'{"title": "Book1",  "pages": [{"title": "Book1", "body": "Text1"}, \
{"title": "Einleitung", "toctitle": "zur Eil", "body": "BAla"}], \
"info": {"AUTOREN": "x"}}'

If the title of a page is the booktitle, then the body will be included in the
generated startpage.
'''

from __future__ import absolute_import
import os
import json
import logging
from . import Action
from bookhelper.utils import template_from_info, on_no_errors


class CreateAction(Action):

    def validate(self):
        jsrc = getattr(self.conf, u"json_source", None)
        if not jsrc:
            self.errors.append(u"No json source")
            return

        try:
            self.bookdata = json.loads(jsrc)
        except json.decoder.JSONDecodeError, e:
            self.errors.append(unicode(e))
            return
        for key in (u'title', u'info', u'pages'):
            v = self.bookdata.get(key, None)
            if not v:
                self.errors.append(u"Missing key: %s" % key)

    @on_no_errors
    def save_page(self, title, content):
        logging.debug(u"Try save page: %s" % title)
        page = self.site.Pages[title]
        if page.text() and not self.conf.force_overwrite:
            self.errors.append(u"Page already exists: %s" % page)
            return
        page.save(content)

    def mk_page(self, page):
        txt = u"\n%s\n" % page[u'body']
        self.save_page(os.path.join(self.title, page[u'title']), txt)

    def mk_toc(self):
        toc = u'\n==Inhaltsverzeichnis==\n'
        toc += u'\n<div class="BookTOC">\n'
        for page in self.pages:
            title = page[u'title']
            toctitle = page.get(u'toctitle', title)
            toc += u"\n# [[%s|%s]]\n" % (
                os.path.join(self.title, title),
                toctitle)
        toc += u"\n</div>\n"
        return toc

    def mk_book_page(self):
        txt = u''
        tmpl = template_from_info(self.bookdata[u'info'])
        if tmpl:
            txt += tmpl
        else:
            self.errors.append(u"No valid info found")
            return
        titlepagelist = [
            p for p in self.pages
            if self.title == p[u'title']]
        if titlepagelist:
            titlepage = titlepagelist[0]
            txt += u"\n %s \n " % titlepage[u'body']
            self.pages.pop(self.pages.index(titlepage))

        txt += u"\n%s" % self.mk_toc()
        txt += u"\n[[Kategorie:Buch]]"
        self.save_page(self.title, txt)

    def run(self):
        self.site = self.login()
        self.title = self.bookdata[u'title']
        self.pages = self.bookdata[u'pages']
        self.book_page = self.mk_book_page()
        for page in self.pages:
            self.mk_page(page)

