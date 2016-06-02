
from __future__ import absolute_import
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
        return[{u'*':  self._text}]


class SiteMock(object):
    def __init__(self):
        self.host = u""
        self.Pages = {
            u'Page1': PageMock(
                u'''Text1
                <div class="BookTOC">
# [[A|A]]
# [[B_2|B]]
                </div>
                '''),
            u'A': PageMock(u"A Text"),
            u'B_2': PageMock(u"B Text"),
        }

    def api(self, action, **kwargs):
        if action == u"query":
            return {
                u'query': {
                    u'pages':{
                        u'1':    {
                            u'flagged': {u'stable_revid': u"1"}
                        }
                    }
                }
            }

        pass



class TestInit(TestCase):
    def setUp(self):
        self.site = SiteMock()

    def test_x(self):

        book = Book(self.site, u"Page1", u"live")
        self.assertEqual(book.book_page.title, u"Page1")
        self.assertEqual(book.book_page.text.strip(), u'''Text1
                <div class="BookTOC">
# [[A|A]]
# [[B_2|B]]
                </div>''')
        self.assertEqual(book.toc[0].target,u'A')
        self.assertEqual(book.toc[1].target,u'B_2')
        self.assertEqual(book.toc[1].page.friendly_title,u'B 2')
        self.assertEqual(book.errors,[])
