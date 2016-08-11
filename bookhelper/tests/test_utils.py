from unittest import TestCase
# from unittest import mock

from bookhelper.utils import template_from_info


class TestUtils(TestCase):
    #def setUp(self):
    #    self.site = SiteMock()

    def test_template_from_info1(self):
        t = template_from_info({
            'ABSTRACT': 'Die Beschreibung',
            'AUTOREN' : 'Autor'
        })
        self.assertEqual(t,
'''{{Bookinfo\n|ABSTRACT = Die Beschreibung\n|AUTOREN = Autor\n}}\n''')
