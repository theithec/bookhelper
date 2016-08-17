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
    api_url = "handbuch.local"
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
        self.is_saved = False

    def text(self):
        return self._text

    def revisions(self, **kwargs):
        return[{'*':  self._text, 'revid': 1}]

    def save(self, text, *args, **kwargs):
        self._text = text
        self.site.Pages[self.title] = self
        pass # if self.title == "Testbook1/0.1":

        self.is_saved = True


    def __str__(self):
        return self._text

class DDict(dict):

    def __getitem__(self, item):
        try:
            i =  super().__getitem__(item)
            if not i.is_saved:
               i._text = ""
            return i

        except KeyError:
            self[item] =  PageMock("")
            return self[item]

    def get(self, item, fallback):
        raise Exception("GET USED")
        #return super().get(self._key(item), fallback)

    def __setitem__(self, i2tem, value):
        #print("VAL",i2tem,  value)
        super().__setitem__(i2tem, value)
        value.title = i2tem

    def __str__(self):
        return ", ".join([k for k in self.keys()])

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
        for v in self.Pages.values():
            v.is_saved = True

    def login(self, *args, **kwargs):
        return self

    def upload(self, *args, **kwargs):
        return {
            'result': 'Success'
        }

    def get_token(self, *args, **kwargs):
        return ""

    def api(self, *args, **kwargs):
        #print("API", args, kwargs)
        action = args[0] if len(args)>0 else kwargs['action']

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
