import json

TESTBOOK1_TXT = '''{{Bookinfo
|AUTOREN = AuthorName1, AUthorName2
|ABSTRACT = ABstractText
}}

This is about the book.

<div class="BookTOC">
# [[Testbook1/Page1|Page1]]
# [[Testbook1/Page2|Page2]]
</div>'''


TESTBOOK1_PAGE1_TXT = '''
Text2.
More Text.
Even more
'''

TESTBOOK1_PAGE2_TXT =  TESTBOOK1_PAGE1_TXT

TESTBOOK2_TXT = '''{{Bookinfo
|HERAUSGEBER = AuthorName1, AUthorName2
|ABSTRACT = ABstractText
}}

This is about the book.

<div class="BookTOC">
# [[Testbook2/Page_1|Page 1]]
# [[Testbook2/Page 2|Page_2]]
</div>'''



JSON_SRC =  json.dumps({
    'title': 'Importbook',
    'info': {'abstract': 'About an import'},
    'pages': [
        {'title': 'Page1', 'body': 'Text'},
        {'title': 'Page2', 'body': 'Text2'}
    ],

})

class Conf:
    force_overwrite = False
    no_https = False
    api_url = ""
    export = ['all']
    book = "Testbook1"
    version = "live"
    user = ""
    password = ""
    tmp_path = "/tmp"
    printpage_title = "Printpage"
    no_doi = True
    json_source = JSON_SRC
    dc_symbol = ""
    dc_password = ""
    dc_prefix = "test"
    dc_identifier = "ident"

class PageMock(object):
    def __init__(self, text):
        self._text = text

    def text(self):
        return self._text

    def revisions(self, **kwargs):
        return[{'*':  self._text}]

    def save(self, text, *args, **kwargs):
        self._text = text

    def __str__(self):
        return self.title

class DDict(dict):

    def __getitem__(self, item):
        try:
            return super().__getitem__(item)
        except KeyError:
            self[item] =  PageMock("")
            return self[item]

    def get(self, item, fallback):
        raise Exception("GET USED")
        #return super().get(self._key(item), fallback)

    def __setitem__(self, i2tem, value):
        super().__setitem__(i2tem, value)
        value.title = i2tem

class SiteMock(object):
    def __init__(self):
        self.host = ""
        self.Pages = DDict({
            'Testbook1': PageMock(TESTBOOK1_TXT),
            'Testbook1/Page1': PageMock(TESTBOOK1_PAGE1_TXT),
            'Testbook1/Page2': PageMock(TESTBOOK1_PAGE2_TXT),
            'Testbook2': PageMock(TESTBOOK2_TXT),
            'Testbook2/Page_1': PageMock(TESTBOOK1_PAGE1_TXT),
            'Testbook2/Page_2': PageMock(TESTBOOK1_PAGE2_TXT),
        })

    def login(self, *args, **kwargs):
        return self
    def upload(self, *args, **kwargs):
        return {
            'result': 'Success'
        }

    def api(self, *args, **kwargs):
        action = args[0]

        if action == "query":
            return {
                'query': {
                    'pages':{
                        '1':    {
                            'flagged': {'stable_revid': "1"},
                            'fullurl': "/dev/null"
                        }
                    }
                }
            }
        elif action == "parse":
            return {
                'parse': {
                    'text':{
                        '*': "Text1"
                    }
                }
            }
