u'''versionizer.py

Creates new version of a book
'''
from __future__ import absolute_import
import os
from bs4 import BeautifulSoup
from bookhelper import Book,  doi, utils
from . import BookAction


class VersionizeAction(BookAction):
    def validate(self):
        if not self.conf.no_doi:
            args = [u"dc_symbol", u"dc_password", u"dc_prefix", u"dc_identifier", ]
            for arg in args:
                if getattr(self.conf, arg, None) is None:
                    self.errors.append(u"Missing argument: %s" % arg)

            bookdoi = doi.BookDoi(self.conf)
            bookdoi.validate()
            if not bookdoi.errors:
                self.doi = bookdoi.doi
            self.errors += bookdoi.errors

        site = self.login()
        super(VersionizeAction, self).validate(site)

    def build_book(self, site):
        self.book = Book(site, self.conf.book, u"live")

    def versionized_template(self):
        doi = getattr(self, u'doi', None)
        if doi:
            self.book.info[u'DOI'] = doi
        return utils.template_from_info(self.book.info)

    def versionized_bookpage_text(self):
        txt = self.book.book_page.text
        txt = (txt[:self.book.template_startpos] +
               self.versionized_template() +
               txt[self.book.template_endpos:])
        soup = BeautifulSoup(txt, u'html.parser')
        toc = soup.find(u'div', class_=u'BookTOC')
        content = toc.contents[0]
        stable_content = os.linesep
        for item in self.book.toc:
            stable_content += (u"#"*item.depth) + item.stable_link + os.linesep

        content.replaceWith(stable_content)
        return soup.decode(formatter=None)

    def run(self):
        version_page_txt = self.versionized_bookpage_text()
        pagetitle = u'%s/%s' % (self.book.book_page.title, self.conf.version)
        self.site = self.login()
        version_page = self.site.Pages[pagetitle]
        if version_page.text() and not self.conf.force_overwrite:
            self.errors.append(u"Page already exists")
        else:
            version_page.save(version_page_txt)
