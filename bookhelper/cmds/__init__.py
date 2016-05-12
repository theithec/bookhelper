import mwclient
from bookhelper import on_no_errors, Book


class Action(object):

    def __init__(self, conf):
        self.errors = []
        self.conf = conf

    def validate(self, *args, **kwargs):
        raise NotImplementedError

    def run(self, *args, **kwargs):
        raise NotImplementedError


class BookAction(Action):

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
        except Exception as e:
            self.errors.append('Login failed ' + str(e))

    def get_site(self):
        site_arg = None
        if self.conf.no_https:
            site_arg = ("http", self.conf.api_url, )
        else:
            site_arg = self.conf.api_url

        # @todo handle exceptions
        site = mwclient.Site(site_arg)

        return site
