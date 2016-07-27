from bookhelper import export, EXPORTKEYS
from bookhelper.utils import on_no_errors
from . import  SiteAction

class PublishAction(SiteAction):
    def init(self):
        self.book = ExistingBook(self.site, self.conf.book, self.conf.version)

    def run(self):
        print("RUN") #pass
        print ("\n".join([str(t) for t in self.book.toc]))
        print (self.book.info)
        self.errors += self.book.errors

    def validate(self, site=None):
        if self.conf.export == ['all']:
            self.conf.export = EXPORTKEYS
        if not set(self.conf.export).issubset(EXPORTKEYS):
            self.errors.append(
                "%s is not a subset of %s" % (self.conf.export, EXPORTKEYS))

    def run(self, site=None):
        self.validate()
        self.export_all()

    @on_no_errors
    def export_all(self):
        if "print" in self.conf.export:
            export.PRINTExport.print_version_title = self.conf.printpage_title
        kwargs = {
            'site': self.site,
            'overwrite': self.conf.force_overwrite or self.conf.version == 'live',
            'title': self.book.book_page.raw_title,
            'friendly_title': self.book.book_page.friendly_title,
            'src': self.book.get_src(),
            'info': self.book.info,
            'tmp_path': self.conf.tmp_path,
        }
        #print("KWARGS", kwargs)
        for exportkey in self.conf.export:
            Export = getattr(export, exportkey.upper()+"Export")
            self.errors += Export(**kwargs).errors
