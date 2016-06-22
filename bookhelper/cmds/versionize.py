'''versionizer.py

Creates new version of a book
'''
import os
from bs4 import BeautifulSoup
from bookhelper import Book,  doi, utils
from . import BookAction


class VersionizeAction(BookAction):
    def validate(self, site=None):
        super().validate(site)
        if not self.conf.no_doi:
            #import sys; sys.exit(self.conf)
            bookdoi = doi.BookDoi(self.conf, self.book )
            bookdoi.validate()
            if not bookdoi.errors:
                self.doi = bookdoi.doi
                self.datacite_kwargs = bookdoi.datacite_kwargs

            self.errors += bookdoi.errors

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

    def run(self, site=None):
        version_page_txt = self.versionized_bookpage_text()
        pagetitle = '%s/%s' % (self.book.book_page.title, self.conf.version)
        self.site = site or self.login()
        version_page = self.site.Pages[pagetitle]
        #result = site.api('parsegtgt', prop='coordinates', titles='Oslo|Copenhagen')
        if version_page.text() and not self.conf.force_overwrite:
            self.errors.append("Page already exists")
        else:
            version_page.save(version_page_txt)
            if not self.conf.no_doi:
                result = self.site.api("query", titles=pagetitle, prop="info",
                                    inprop="url")
                fullurl = list(result['query']['pages'].values())[0]['fullurl']
                bookdoi = doi.BookDoi(self.conf, self.book)
                bookdoi.set_doi(fullurl, self.doi, self.datacite_kwargs)
