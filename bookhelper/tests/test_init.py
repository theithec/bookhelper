
from unittest import TestCase
# from unittest import mock

from mwclient import Site
from bookhelper import Book
#Site.login=mock.MagicMock(return_value=True)

class PageMock(object):
    def __init__(self, text):
        self._text = text

    def text(self):
        return self._text

    def revisions(self, **kwargs):
        return[{'*':  self._text}]


class SiteMock(object):
    def __init__(self):
        self.host = ""
        self.Pages = {
            'Page1': PageMock(
                '''Text1
                <div class="BookTOC">
# [[A|A]]
# [[B_2|B]]
                </div>
                '''),
            'A': PageMock("A Text"),
            'B_2': PageMock("B Text"),
        }

    def api(self, action, **kwargs):
        if action == "query":
            return {
                'query': {
                    'pages':{
                        '1':    {
                            'flagged': {'stable_revid': "1"}
                        }
                    }
                }
            }

        pass



class TestInit(TestCase):
    def setUp(self):
        self.site = SiteMock()

    def test_x(self):

        book = Book(self.site, "Page1", "live")
        self.assertEqual(book.book_page.title, "Page1")
        self.assertEqual(book.book_page.text.strip(), '''Text1
                <div class="BookTOC">
# [[A|A]]
# [[B_2|B]]
                </div>''')
        self.assertEqual(book.toc[0].target,'A')
        self.assertEqual(book.toc[1].target,'B_2')
        self.assertEqual(book.toc[1].page.friendly_title,'B 2')
        self.assertEqual(book.errors,[])
