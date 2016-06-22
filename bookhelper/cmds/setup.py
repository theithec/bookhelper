
'''setup.py

Prepare the mediawiki.
For now it only adds/resets the `bookinfo` template
'''

import sys

from . import Action

class SetupAction(Action):

    def validate(self):
        site = self.login()

    def run(self):
        self.site = self.login()
        bookinfo = self.site.Pages['Template:Bookinfo']
        if bookinfo.text() and not self.conf.force_overwrite:
            self.errors.append("Template:Bookinfo already exists")
        else:
            bookinfo.save("""
<includeonly>
{{#tag:bookinfo
|{{{ABSTRACT}}}
|contributors="{{{KONTRIBUTOREN}}}"
|authors="{{{AUTOREN}}}"
|stand="{{{STAND}}}"
|doi="{{{DOI}}}"
}}
</includeonly>
<noinclude>
Diese Vorlage erzeugt einen Buchtitel mit Autoren, Kontributen, Abstract und Links zu PDF und Druckversion.
</noinclude>
<includeonly>{|
</includeonly>
""")

