import os
from unittest import TestCase
# from unittest import mock

from mwclient import Site
from datacite.errors import DataCiteServerError
from bookhelper.cmds import publish, versionize, create
from bookhelper import EXPORTKEYS,doihelper
from . import PageMock, SiteMock, Conf


class TestActions(TestCase):
    def setUp(self):
        self.site = SiteMock()
        self.conf = Conf()
        PageMock.site = self.site


    def publish(self):
        publish.PublishAction.sitemock = self.site
        p = publish.PublishAction(self.conf)
        return p

    def versionize(self):
        #c.version = "0.1"
        #doi.BookDoi.test_mode = True
        versionize.VersionizeAction.sitemock = self.site
        v = versionize.VersionizeAction(self.conf)
        return v
        #b = doihelper.DoiHelper(c,  v.book)
        #b.doi = "10.5072/x/y"
        #b._get_bookdata(v.book)
        #self.assertEqual(b.errors, [])


    def create(self):
        create.CreateAction.sitemock = self.site
        a = create.CreateAction(self.conf)
        return a
    def test_publish_ok(self):
        p = self.publish()
        self.assertEqual(p.errors, [])
        for t in  EXPORTKEYS:
            if t == "print":
                continue
            p =  os.path.join(self.conf.tmp_path, self.conf.book + "_live." + t)
            self.assertTrue(os.path.exists(p), p)

        pages = self.site.Pages.keys()
        printpage =  "{0.book}/{0.printpage_title}".format(self.conf)
        self.assertIn(printpage, pages, str(pages))



    def test_publish_fail(self):
        self.conf.book = "Neverbook"
        p = self.publish()
        self.assertEqual(p.errors,  ['No Page with this title was found: "Neverbook"'])

    def test_versionize(self):
        self.conf.version = "0.1"
        v = self.versionize()
        self.assertEqual(v.errors, [])

    def test_create(self):
        self.conf.version = "live"
        c = self.create()
        self.assertEqual(c.errors, [])
        self.assertEqual(c.book_page.title, "Importbook")
        pages = self.site.Pages
        self.assertIn("Importbook", pages)
        self.assertIn("Importbook/Page1", pages)
        self.assertIn("Importbook/Page2", pages)
        self.assertEqual(pages["Importbook"].text(),
'''{{Bookinfo
|ABSTRACT = About an import
}}


==Inhaltsverzeichnis==

<div class="BookTOC">
# [[Importbook/Page1|Page1]]
# [[Importbook/Page2|Page2]]

</div>

[[Kategorie:Buch]]''')
        self.assertEqual(pages["Importbook/Page1"].text(), "\nText\n")
        self.assertEqual(pages["Importbook/Page2"].text(), "\nText2\n")


    def test_create_fail(self):
        self.conf.version = "live"
        v = self.create()
        self.assertEqual(v.errors, [])
        v = self.create()
        self.assertEqual(v.errors, ['Page already exists: Importbook'])



