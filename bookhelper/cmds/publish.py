u'''publish.py

runs `exportexports` on a book.
'''
from __future__ import absolute_import
import sys
import logging
import re

from bookhelper import export, EXPORTKEYS
from . import BookAction

def get_pagetext_from_item(item, found_references):
    txt = u"\n\n=%s=\n\n" % item.page.friendly_title
    txt += item.page.text
    txt, numsubs = re.subn(
        u"(=+\s*Einzelnachweise?\s*=+|<references\s*\/>)", u"", txt)
    if numsubs > 0:
        found_references = True
    return txt, found_references


def get_book_src(book):
    found_references = False
    txt = u''
    for item in book.toc:
        if item.depth > 1:
            continue
        ptxt, found_references = get_pagetext_from_item(item, found_references)
        txt += ptxt

    if found_references:
        txt += u"= Einzelnachweise =\n<references/>\n\n"

    return txt


def book_exports(exportkeys, exportkwargs):
    u'''Run exports specified by exportkeys for a book.

        Args:
            site (Site): Mwclient site object
            book(Book): Book
            exportkeys(list): Keys for exports. See EXPORTKEYS
    '''
    errors = []
    for exportkey in exportkeys:
        Export = getattr(export, exportkey.upper()+u"Export")
        errors += Export(**exportkwargs).errors
    return errors


class PublishAction(BookAction):

    def validate(self):
        site = self.get_site()
        self.login(site)
        if self.conf.export == [u'all']:
            self.conf.export = EXPORTKEYS
        if not set(self.conf.export).issubset(EXPORTKEYS):
            self.errors.append(
                u"%s is not a subset of %s" % (self.conf.export, EXPORTKEYS))
        super(PublishAction, self).validate(site)

    def run(self):
        site = self.get_site()
        self.login(site)
        if u"print" in self.conf.export:
            export.PRINTExport.print_version_title = self.conf.printpage_title

        kwargs = {
            u'site': site,
            u'overwrite': self.conf.force_overwrite or self.conf.version == u'live',
            u'title': self.book.book_page.title,
            u'friendly_title': self.book.book_page.friendly_title,
            u'src': get_book_src(self.book),
        }
        self.errors += book_exports(self.conf.export, kwargs)
        return u"FAILED" if self.errors else u"SUCCESS"
