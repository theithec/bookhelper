u''' cmds/__init__.py

Base action classes. An action is meant to be called from commandline
or from another action.
Actions that may be called as a queued command must not have the mwclient.site
as an attribute (it's not serializable) before the `run` method is called.

'''

from __future__ import absolute_import
import mwclient
from bookhelper import on_no_errors, Book


class Action(object):

    def __init__(self, conf):
        self.errors = []
        self.conf = conf
        self.conf.force_overwrite = getattr(self.conf, u'force_overwrite', False)
        self._site = None

    def validate(self, *args, **kwargs):
        raise NotImplementedError

    def run(self, *args, **kwargs):
        raise NotImplementedError

    def get_site(self):
        site_arg = None
        site = None
        if self.conf.no_https:
            site_arg = (u"http", self.conf.api_url, )
        else:
            site_arg = self.conf.api_url

        # @todo handle exceptions
        try:
            site = mwclient.Site(site_arg)
        except Exception, e:
            self.errors.append(unicode(e))

        return site

    @on_no_errors
    def login(self):
        site = self.get_site()
        try:
            site.login(self.conf.user, self.conf.password)
        except Exception, e:
            self.errors.append(u'Login failed ' + unicode(e))
        return site


class BookAction(Action):

    def build_book(self, site):
        self.book = Book(site, self.conf.book, self.conf.version)

    def validate(self, site):
        site = self.login()
        if site:
            self.build_book(site)
            self.errors += self.book.errors


