import mwclient
from bookhelper import ExistingBook

class Action(object):
    '''BaseAction'''

    def __init__(self, conf):
        self.result = None
        self.conf = conf
        self.errors = []
        self.init()
        if not self.errors:
            self.run()


class SiteAction(Action):
    '''An Action that interacts with an mediawiki'''
    def init(self):
        self.login()

    def login(self):
        site_arg = None
        self.site =  getattr(self, "sitemock", None)
        if self.site:
            return # test with sitemock
        if self.conf.no_https:
            site_arg = ("http", self.conf.api_url, )
        else:
            site_arg = self.conf.api_url

        try:
            self.site = mwclient.Site(site_arg)
            self.site.login(self.conf.user, self.conf.password)
        except Exception as e:
            self.errors.append(str(e))


class ExistingBookAction(SiteAction):
    def init(self):
        super().init()



class CreateBookAction(object):pass
