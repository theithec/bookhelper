'''versionizer.py

Creates new version of a book
'''
import os
import sys
from bs4 import BeautifulSoup
from bookhelper import Book,  doi
from . import BookAction

class VersionizeAction(BookAction):
    def validate(self):
        if not self.conf.no_doi:
            args = ["dc_symbol", "dc_password", "dc_prefix", "dc_identifier",
                    "dc_version"]
            for arg  in args:
                if  getattr(self.conf,arg, None) is None  :
                    self.errors.append("Missing argument: %s" % arg )

            bookdoi = doi.BookDoi(self.conf)
            bookdoi.validate()
            self.errors += bookdoi.errors

        site = self.get_site()
        super().validate(site)

    def build_book(self, site):
        self.book = Book(site, self.conf.book, "live")

    def versionized_bookpage_text(self ):
        txt = self.book.book_page.text
        soup = BeautifulSoup(txt, 'html.parser')
        toc = soup.find('div', class_='BookTOC')
        content = toc.contents[0]
        stable_content = os.linesep
        for item in self.book.toc:
            stable_content += ("#"*item.depth) + item.stable_link + os.linesep

        content.replaceWith(stable_content)
        return soup.decode(formatter=None)

    def run(self ):
        version_page_txt = self.versionized_bookpage_text()
        pagetitle = '%s/%s' % (self.book.book_page.title, self.conf.version)
        site = self.get_site()
        self.login(site)
        version_page = site.Pages[pagetitle]
        version_page.save(version_page_txt)
        return "FAILED" if self.errors else "SUCCESS"


