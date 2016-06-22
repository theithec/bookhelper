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
'''{{#
|AUTOREN = AuthorName1, AUthorName2
|ABSTRACT = ABstractText
}}

Text1

<div class="BookTOC">
# [[A|A]]
# [[B_2|B]]
</div>'''),
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


