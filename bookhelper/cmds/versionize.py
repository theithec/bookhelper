'''versionizer.py

Creates new version of a book
'''
import os
from bs4 import BeautifulSoup
from bookhelper import Book,  doi, utils
from . import BookAction


class VersionizeAction(BookAction):
    def validate(self):
        if not self.conf.no_doi:
            args = ["dc_symbol", "dc_password", "dc_prefix", "dc_identifier", ]
            for arg in args:
                if getattr(self.conf, arg, None) is None:
                    self.errors.append("Missing argument: %s" % arg)

            bookdoi = doi.BookDoi(self.conf)
            bookdoi.validate()
            if not bookdoi.errors:
                self.doi = bookdoi.doi
            self.errors += bookdoi.errors

        site = self.login()
        super().validate(site)

    def build_book(self, site):
        self.book = Book(site, self.conf.book, "live")

    def versionized_template(self):
        doi = getattr(self, 'doi', None)
        if doi:
            self.book.info['DOI'] = doi
        return utils.template_from_info(self.book.info)

    def versionized_bookpage_text(self):
        txt = self.book.book_page.text
        txt = (txt[:self.book.template_startpos] +
               self.versionized_template() +
               txt[self.book.template_endpos:])
        soup = BeautifulSoup(txt, 'html.parser')
        toc = soup.find('div', class_='BookTOC')
        content = toc.contents[0]
        stable_content = os.linesep
        for item in self.book.toc:
            stable_content += ("#"*item.depth) + item.stable_link + os.linesep

        content.replaceWith(stable_content)
        return soup.decode(formatter=None)

    def run(self):
        version_page_txt = self.versionized_bookpage_text()
        pagetitle = '%s/%s' % (self.book.book_page.title, self.conf.version)
        self.site = self.login()
        version_page = self.site.Pages[pagetitle]
        version_page.save(version_page_txt)
        return "FAILED" if self.errors else "SUCCESS"
