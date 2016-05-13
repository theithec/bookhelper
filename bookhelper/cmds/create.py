'''
python -m bookhelper -c bookhelper.cfg create '{"title": "CBook2",  "pages": [{"title": "CBook", "body": "p1"}, {"title": "Einleitung", "toctitle": "zur Eil", "body": "BAla"}], "info": {"AUTOREN": "x"}}'
'''
import os
import json
import logging
from . import Action
from bookhelper.utils import template_from_info
class CreateAction(Action):

    def validate(self):
        jsrc = getattr(self.conf, "json_source", None)
        if not jsrc:
            self.errors.append("No json source")
            return

        try:
            self.bookdata = json.loads(jsrc)
            print(self.bookdata)
        except json.decoder.JSONDecodeError as e:
            self.errors.append(str(e))
            return
        for key in ('title', 'info', 'pages'):
            v = self.bookdata.get(key, None)
            if not v:
                self.errors.append("Missing key: %s" % key)

    def save_page(self, title, content):
        logging.debug("Try save page: %s" % title)
        page = self.site.Pages[title]
        print ("PT", page.text())
        if page.text():
            self.errors.append("Page already exists: %s" % page)
            return
        page.save(content)

    def mk_page(self, page):
        txt = " # %s #\n" % page['title']
        txt += "\n%s\n" % page['body']
        self.save_page(os.path.join(self.title, page['title']), txt)

    def mk_toc(self):
        toc = '\n<div class="BookTOC">\n'
        for page in self.pages:
            title = page['title']
            toctitle = page.get('toctitle', title)
            toc += "\n# [[%s|%s]]\n" % (toctitle, title)
        toc += "\n</div>\n"
        return toc


    def mk_book_page(self):
        body = ""
        txt = '# {0.title} #\n\n'.format(self)
        tmpl= template_from_info(self.bookdata['info'])
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
        self.save_page(self.title, txt)


    def run(self):
        import pdb; pdb.set_trace()
        self.site = self.login()
        print("SESI", self.site)
        self.title = self.bookdata['title']
        self.pages = self.bookdata['pages']
        self.book_page = self.mk_book_page()
        for page in self.pages:
            self.mk_page(page)

