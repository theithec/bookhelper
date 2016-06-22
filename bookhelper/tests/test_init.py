from unittest import TestCase
# from unittest import mock

from mwclient import Site
from bookhelper import Book
from . import PageMock, SiteMock
#Site.login=mock.MagicMock(return_value=True)




class TestInit(TestCase):
    def setUp(self):
        self.site = SiteMock()

    def test_book(self):

        book = Book(self.site, "Page1", "live")
        print("BOOK", book)
        print("BOOKPAGE", book.book_page)
        print("BOOKTOC", book.toc)
        self.assertEqual(book.errors, [])
        self.assertEqual(book.book_page.title, "Page1")
        self.assertEqual(book.book_page.text.strip(),
'''{{#
|AUTOREN = AuthorName1, AUthorName2
|ABSTRACT = ABstractText
}}

Text1

<div class="BookTOC">
# [[A|A]]
# [[B_2|B]]
</div>''')

        self.assertEqual(book.toc[0].target,'A')
        self.assertEqual(book.toc[1].target,'B_2')
        self.assertEqual(book.toc[1].page.friendly_title,'B 2')
