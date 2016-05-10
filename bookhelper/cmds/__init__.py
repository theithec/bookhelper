from __future__ import absolute_import
import mwclient
from bookhelper import on_no_errors, Book


class Action(object):
    is_book_action = False

    def __init__(self, conf):
        self.errors = []
        self.conf = conf


class BookAction(Action):
    is_book_action = True

    def build_book(self, site):
        self.book = Book(site, self.conf.book, self.conf.version)

    def validate(self, site):
        self.login(site)
        if site:
            self.build_book(site)
            self.errors += self.book.errors

    @on_no_errors
    def login(self, site):
        try:
            site.login(self.conf.user, self.conf.password)
        except Exception, e:
            self.errors.append(u'Login failed ' + unicode(e))

    def get_site(self):
        site_arg = None
        if self.conf.no_https:
            site_arg = (u"http", self.conf.api_url, )
        else:
            site_arg = self.conf.api_url

        # @todo handle exceptions
        site = mwclient.Site(site_arg)

        return site
