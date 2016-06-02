# -*- coding: utf-8 -*-
u'''export.py

The actions to create different formats from a handbuch.io-`book` live here

'''
from __future__ import with_statement
from __future__ import absolute_import
import os
from os.path import abspath, dirname, isfile
import sys
import logging
from datetime import datetime
import pypandoc
from bs4 import BeautifulSoup

from .utils import get_siteurl
from io import open


class Export(object):

    def __init__(self, site, src, title, friendly_title, info, tmp_path,
                 overwrite=True):
        self.site = site
        self.src = src
        self.title = title
        self.friendly_title = friendly_title
        self.info = info
        self.overwrite = overwrite
        self.errors = []
        self.tmp_path = tmp_path
        self.prestart()

    def prestart(self):
        self.start()

    def start(self):
        if not self.errors:
            self._create()


class PRINTExport(Export):
    print_version_title = u"_Printversion"

    def _create(self):
        title = u'%s/%s' % (self.title, self.print_version_title)
        logging.debug(u"Printversion title: %s" % (title))
        printpage = self.site.Pages[title]
        if not self.overwrite and printpage.text():
            self.errors.append(u'Page "%s" already exists' % title)
            return

        printpage.save(self.src)


class PandocExport(Export):

    def prestart(self):
        self.outfilename = (
            u"%s.%s" % (self.title, self.outformat)
        ).replace(u"/", u"_")
        self.outpath = os.path.join(self.tmp_path, self.outfilename)
        if not self.overwrite and isfile(self.outpath):
            self.errors.append(u'File "%s" already exists' % self.outfilename)
            return

        os.environ[u"HOME"] = self.tmp_path  # pandoc needs a $HOME
        self.start()

    def get_pandoc_params(self):
        args = [self.get_soup().prettify(), self.outformat]
        kwargs = {
            'format': u'html',
            'outputfile': self.outpath}
        return args, kwargs

    def get_soup(self):
        result = self.site.api(
            u"parse", text=self.src)
        txt = result[u'parse'][u'text'][u'*']
        soup = BeautifulSoup(txt, u'html.parser')
        [x.extract() for x in soup.findAll(u'span', class_=u"mw-editsection")]
        # One idea was to use a custom toc. Delete the old one:
        toc = soup.find(u'div', attrs={u'id': u'toc'})
        if toc:
            toc.extract()

        site_url = get_siteurl(self.site)
        # https://github.com/jgm/pandoc/issues/1886
        # mediawikis <h*><span class="mw-headline" id="INTERNAL TARGET">...
        # breaks pandoc
        # but without the ids internal links do not work.
        # so we copy those ids to their parents (the real headline tag)
        # before deleting
        for tag in soup():
            c = tag.get(u'class')
            if c and u"mw-headline" in c:
                i = tag.get(u"id")
                tag.parent[u'id'] = i

            del tag[u'id']

            c = tag.get(u'src')
            if c and c.startswith(u"/"):
                tag[u'src'] = u"".join((site_url, c),)

        with open(os.path.join(self.tmp_path, u"src.html"), u"w") as f:
            f.write(soup.prettify()) #.encode("utf-8")))

        return soup

    def upload(self):
        msg = u'%s: "%s" als %s' % (
            datetime.now().strftime(u"%Y-%M-%d %h:%M"),
            self.friendly_title,
            self.outformat)
        outfile = open(self.outpath, u"rb")
        try:
            res = self.site.upload(
                outfile, self.outfilename, msg, ignore=True)
        except:
            self.errors.append(unicode(u"UPLOAD-ERROR: " + unicode(sys.exc_info())))
            return

        if res[u'result'] != u"Success":
            self.errors.append(u"Upload failed for %s" % self.outfilename)

    def _create(self):
        args, kwargs = self.get_pandoc_params()
        try:
            pypandoc.convert(*args, **kwargs)
        except:
            self.errors.append(unicode(u"PANDOC-ERROR: " + unicode(sys.exc_info())))
            return

        self.upload()


class PDFExport(PandocExport):
    outformat = "pdf"

    def get_pandoc_params(self):
        args, kwargs = super(PDFExport, self).get_pandoc_params()
        kwargs[u'extra_args'] = [
            '--latex-engine=xelatex',
            '--chapters',
            #'--verbose',
            '--standalone',
            '--toc',
            '--template=%s/template.latex' % dirname(abspath(__file__)),
            # '-M', 'documentclass=book',
            '-M', u'author="%s"' % self.info.get(
                u"AUTOREN",
                self.info.get(u"HERAUSGEBER", u"")),
            '-M', u'include-before="Wichtige Hinweise"',
            '-M', u'subtitle="%s"' % self.info.get(u"ABSTRACT"),
            '-M', u'lang="german"',
            '-M', u'mainlang="german"',
            '-M', u'title="%s"' % self.friendly_title
        ]
        return args, kwargs


class ODTExport(PandocExport):
    outformat = u"odt"


class MARKDOWNExport(PandocExport):
    outformat = u"markdown"
