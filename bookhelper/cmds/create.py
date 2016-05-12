import json
from . import Action

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
        for key in ('title', 'info', 'toc', 'pages'):
            v = self.bookdata.get(key, None)
            if not v:
                self.errors.append("Missing key: %s" % key)

    def mk_page(self, title):
        body = self.pages[title]

    def mk_book_page(self, title):
        body = ""


    def run(self):
        pass
        self.title = self.bookdata['title']
        self.pages = self.bookdata['pages']
        if title in pages:
            self.book_page = self.mk_page(self.title)
        else:
            self.book_page = self.mk_book_page()

