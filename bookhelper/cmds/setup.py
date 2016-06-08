
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
<includeonly>{|
{{#if:{{{ABSTRACT|}}}|
    {{!}} colspan="2" {{!}} {{{ABSTRACT}}}
}}
|-
{{#if:{{{AUTOREN|}}}|
    {{!}} '''Autoren:'''
    {{!}} {{{AUTOREN}}}
}}
|-
{{#if:{{{HERAUSGEBER|}}}|
    {{!}} '''Herausgeber:'''
    {{!}} {{{HERAUSGEBER}}}
}}
|-
{{#if:{{{KONTRIBUTOREN|}}}|
    {{!}} '''Kontributoren:'''
    {{!}} {{{KONTRIBUTOREN}}}
}}
|-
{{#if:{{{STAND|}}} |
    {{!}} '''Stand:'''
    {{!}} {{{STAND}}}
}}
|-
{{#if:{{{DOI|}}} |
    {{!}} '''Doi:'''
    {{!}} {{{DOI}}}
}}
|-
{{#if:{{{VERSION|}}} |
    {{!}} '''Version:'''
    {{!}} {{{VERSION}}}
}}
|}

Zur [[{{PAGENAME}}/_Druckversion|Druckversion]] (alle Kapitel des Buches auf einer Seite).

[[Datei:{{{TITLE}}}_ {{{VERSION}}}.pdf|PDF-Version herunterladen]]

</includeonly>
<noinclude>
Diese Vorlage erzeugt einen Buchtitel mit Autoren, Kontributen, Abstract und Links zu PDF und Druckversion.
</noinclude>
                          """)

