from unittest import TestCase
# from unittest import mock

from mwclient import Site
from bookhelper import ExistingBook
from . import PageMock, SiteMock, TESTBOOK1_TXT
#Site.login=mock.MagicMock(return_value=True)




class TestInit(TestCase):
    def setUp(self):
        self.site = SiteMock()

    def test_book(self):

        book = ExistingBook(self.site, "Testbook1", "live")
        self.assertEqual(book.errors, [])
        self.assertEqual(book.book_page.friendly_title, "Testbook1")
        self.assertEqual(book.book_page.text.strip(), TESTBOOK1_TXT)
        self.assertEqual(book.toc[0].target,'Testbook1/Page1')
        self.assertEqual(book.toc[1].target,'Testbook1/Page2')
        self.assertEqual(book.toc[1].text,'Page2')
