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
            bookdoi = doi.BookDoi(self.conf)
            bookdoi.validate()
            if not bookdoi.errors:
                self.doi = bookdoi.doi
        self.errors += bookdoi.errors
        if self.errors:
            return
        site = self.login()
        super().validate(site)

    def build_book(self, site):
        self.book = Book(site, self.conf.book, "live")

    def versionized_template(self):
        doi = getattr(self, 'doi', None)
        if doi:
            self.book.info['DOI'] = doi

        self.book.info['version'] = self.conf.version
        self.book.info['title'] = self.book.book_page.title

        #import pdb; pdb.set_trace()
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
        if version_page.text() and not self.conf.force_overwrite:
            self.errors.append("Page already exists")
        else:
            version_page.save(version_page_txt)
