'''export.py

The actions to create different formats from a handbuch.io-`book` live here

'''
import os
from os.path import abspath, dirname, isfile
import sys
import logging
from datetime import datetime
import pypandoc
from bs4 import BeautifulSoup

from .utils import get_siteurl


class Export(object):

    def __init__(self, site, src, title, friendly_title, tmp_path, overwrite=True):
        self.site = site
        self.src = src
        self.title = title
        self.friendly_title = friendly_title
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
    print_version_title = "_Printversion"

    def _create(self):
        title = '%s/%s' % (self.title, self.print_version_title)
        logging.debug("Printversion title: %s" % (title))
        printpage = self.site.Pages[title]
        if not self.overwrite and printpage.text():
            self.errors.append('Page "%s" already exists' % title)
            return

        printpage.save(self.src)


class PandocExport(Export):

    def prestart(self):
        self.outfilename = (
            "%s.%s" % (self.title, self.outformat)
        ).replace("/", "_")
        self.outpath = os.path.join(self.tmp_path, self.outfilename)
        if not self.overwrite and isfile(self.outpath):
            self.errors.append('File "%s" already exists' % self.outfilename)
            return

        os.environ["HOME"] = self.tmp_path  # pandoc needs a $HOME
        self.start()

    def get_pandoc_params(self):
        args = [self.get_soup().prettify(), self.outformat]
        kwargs = {
            'format': 'html',
            'outputfile': self.outpath}
        return args, kwargs

    def get_soup(self):
        result = self.site.api(
            "parse", text=self.src)
        txt = result['parse']['text']['*']
        soup = BeautifulSoup(txt, 'html.parser')
        [x.extract() for x in soup.findAll('span', class_="mw-editsection")]
        # One idea was to use a custom toc. Delete the old one:
        toc = soup.find('div', attrs={'id': 'toc'})
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
            c = tag.get('class')
            if c and "mw-headline" in c:
                i = tag.get("id")
                tag.parent['id'] = i

            del tag['id']

            c = tag.get('src')
            if c and c.startswith("/"):
                tag['src'] = "".join((site_url, c),)

        with open(os.path.join(self.tmp_path, "src.html"), "w") as f:
            f.write(str(soup.prettify().encode("utf-8")))

        return soup

    def upload(self):
        msg = '%s: "%s" als %s' % (
            datetime.now().strftime("%Y-%M-%d %h:%M"),
            self.friendly_title,
            self.outformat)
        outfile = open(self.outpath, "rb")
        try:
            res = self.site.upload(
                outfile, self.outfilename, msg, ignore=True)
        except:
            self.errors.append(str("UPLOAD-ERROR: " + str(sys.exc_info())))
            return

        if res['result'] != "Success":
            self.errors.append("Upload failed for %s" % self.outfilename)

    def _create(self):
        args, kwargs = self.get_pandoc_params()
        try:
            pypandoc.convert(*args, **kwargs)
        except:
            self.errors.append(str("PANDOC-ERROR: " + str(sys.exc_info())))
            return

        self.upload()


class PDFExport(PandocExport):
    outformat = "pdf"

    def get_pandoc_params(self):
        args, kwargs = super().get_pandoc_params()
        kwargs['extra_args'] = [
            '--latex-engine=xelatex',
            '--chapters',
            #'--verbose',
            '--standalone',
            '--toc',
            '--template=%s/template.latex' % dirname(abspath(__file__)),
            # '-M', 'documentclass=book',
            '-M', 'author="Tim Heithecker"',
            '-M', 'include-before="Wichtige Hinweise"',
            '-M', 'subtitle="DIe Beschreibung"',
            '-M', 'lang="german"',
            '-M', 'mainlang="german"',
            '-M', 'title="%s"' % self.friendly_title
        ]
        return args, kwargs


class ODTExport(PandocExport):
    outformat = "odt"


class MARKDOWNExport(PandocExport):
    outformat = "markdown"
