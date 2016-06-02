u'''bookhelper

shared classes and functions
'''

from __future__ import absolute_import
import os
import re
import logging
from bs4 import BeautifulSoup

from .utils import (parse_tocline, tocline_external_links_re,
                    tocline_internal_links_re, parse_template_text,
                    on_no_errors, get_siteurl)

EXPORTKEYS = [u'pdf', u'print', u'odt']



class StablePage(object):
    u'''One revesion of every (book)-page should be marked as stable.
       And that revission is to be be used for generating documents/versions.
       However, it's a little bit complicate to receive the stable revision
       via the api. This is what we do here'''

    def __init__(self, site, book,   title):
        self.title = title
        self.friendly_title = self.title.replace(u"_", u" ")
        _wrapped_page = site.Pages[title]

        if not _wrapped_page.text():
            book.errors.append(
                u'No Page with this title was found: "%s"' % self.title)
            return
        r = site.api(u"query", titles=title, prop=u"flagged")
        pages = r[u'query'][u'pages']
        # pages is a dict with one key: the page_id we don't know yet.
        pid = list(pages.keys())[0]
        # page = list(pages.values())[0]
        try:
            self.stable_id = int(pages[pid][u'flagged'][u'stable_revid'])  # jay!
        except KeyError:
            book.errors.append(u'No stable revision found for "%s"' % title)
            return
        self.title = title
        stable_rev = _wrapped_page.revisions(
            startid=self.stable_id,
            endid=self.stable_id,
            expandtemplates=False,
            prop=u"content")
        self.text = list(stable_rev)[0][u'*']
        self.fullurl = os.path.join(
            book.site_url, u'w',
            u'index.php?title={0.title}&stableid={0.stable_id}'.format(self))


class BaseBookTocItem(object):
    u'''
    A TocItem. Expects a line from the "div.BookTOC"-list as input.
    Because it is not possible to create internal link for a specific revision
    in wikitext different handling for "Live"-books and versionized books is
    requiered, therefore two subclasses exist.

    Attributes:
        depth(int): the depth of the entry (as in a nested list)
        target(str): The url or wikitext-internal-link of the item.
        text(str): The linktext of the item.
        book(Book): The book this item belongs to.
        page(StablePage): the StablePage object for the target
    '''

    def __init__(self, site, book, line):
        self.is_valid = False
        self.depth, link_parts = parse_tocline(line, self.item_re)
        self.target = link_parts[0].replace(u" ", u"_")
        if u"#" in self.target:
            return
        self.text = link_parts[1 if len(link_parts) > 1 else 0].strip()
        self.page = StablePage(site, book, self._title())
        self.is_valid = True

    def __str__(self):
        return unicode(self.__dict__)


class LiveBookTocItem(BaseBookTocItem):
    item_re = tocline_internal_links_re

    def __init__(self, site, book, line):
        super(LiveBookTocItem, self).__init__(site, book, line)
        if self.is_valid and not book.errors:
            self.stable_link = (
                u'<span class="plainlinks">' +
                u'[{0.page.fullurl} | {0.text}]'.format(self) +
                u'</span>')

    def _title(self):
        return self.target


class VersionizedBookTocItem(BaseBookTocItem):
    title_re = re.compile(ur'.*title=(.*?)&')
    item_re = tocline_external_links_re

    def _title(self):
        return re.match(self.title_re, self.target).groups()[0]


class Book(object):
    u'''Represents an exisiting handbuch.io-`book`

       Attempts to analyze the toc and the first template
       on the book's start page
    '''

    def __init__(self, site, title, version):
        u'''Build a book.
        Args:
            site (Site): Mwclient site object
            title(str): Booktitle
        '''
        self.errors = []
        self.version = version
        self.site_url = get_siteurl(site)
        if self.version != u"live":
            title = u"/".join((title, self.version))
        self.book_page = StablePage(site, self, title)
        if self.errors:
            return
        u'''if self.errors:
            self.errors.append(
                'No Page with this title was found: "%s"' % self.title)
        '''
        self.info = self._get_info()
        self.toc = self._get_toc(site)

    @on_no_errors
    def _get_toc(self, site):
        u'''re for parsing wikitext  toc link'''
        soup = BeautifulSoup(self.book_page.text, u'html.parser')
        try:
            toctext = soup.find_all(u"div", class_=u"BookTOC")[0].text.strip()
        except IndexError:
            self.errors.append(
                u'No Toc found for book "%s"' % self.book_page.title)
            return
        BookTocItemClz = (
            LiveBookTocItem if self.version == u"live"
            else VersionizedBookTocItem)
        logging.debug(u"TOC: %s" % unicode(toctext))
        toc = []
        for line in toctext.split(os.linesep):
            if not line:
                continue

            item = BookTocItemClz(site, self, line)
            if item.is_valid:
                toc.append(item)

        return toc

    @on_no_errors
    def _get_info(self):
        txt = self.book_page.text
        self.template_startpos = txt.find(u'{{')
        self.template_endpos = txt.find(u'}}') + 2
        inner = txt[self.template_startpos + 2: self.template_endpos - 2]
        d = parse_template_text(inner)
        if not d:
            self.errors.append(
                u'No template found for "%s"' % self.book_page.title)

        return d
