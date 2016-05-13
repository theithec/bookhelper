''' cmds/__init__.py

Base action classes. An action is meant to be called from commandline
or from another action.
Actions that may be called as a queued command must not have the mwclient.site
as an attribute (it's not serializable) before the `run` method is called.

'''

import mwclient
from bookhelper import on_no_errors, Book


class Action(object):

    def __init__(self, conf):
        self.errors = []
        self.conf = conf
        self._site = None

    def validate(self, *args, **kwargs):
        raise NotImplementedError

    def run(self, *args, **kwargs):
        raise NotImplementedError

    def get_site(self):
        site_arg = None
        if self.conf.no_https:
            site_arg = ("http", self.conf.api_url, )
        else:
            site_arg = self.conf.api_url

        # @todo handle exceptions
        site = mwclient.Site(site_arg)

        return site

    @on_no_errors
    def login(self):
        site = self.get_site()
        try:
            site.login(self.conf.user, self.conf.password)
        except Exception as e:
            self.errors.append('Login failed ' + str(e))
        return site


class BookAction(Action):

    def build_book(self, site):
        self.book = Book(site, self.conf.book, self.conf.version)

    def validate(self, site):
        site = self.login()
        if site:
            self.build_book(site)
            self.errors += self.book.errors


