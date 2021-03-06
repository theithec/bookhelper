import os
import re
from bs4 import BeautifulSoup
from .utils import get_siteurl, on_no_errors


EXPORTKEYS = ['odt', 'pdf', 'epub', 'print']


class StablePage(object):
    '''A wrapper around mwclients `Page` to make sure the latest revision
       is also the stable one'''

    def __init__(self, site, title):
        self.site = site
        self.raw_title = title
        self.errors = []
        self.friendly_title = title.replace("_", " ")
        self.wrapped_page = site.Pages[title]
        self.text = self.wrapped_page.text()
        if not self.text:
            self.errors.append(
                'No Page with this title was found: "%s"' % title)
        self.find_stable_id()
        self.compare_stable_and_current()
        self.build_fullurl()

    @on_no_errors
    def build_fullurl(self):
        site_url = get_siteurl(self.site)
        self.fullurl = os.path.join(
            site_url, 'w',
            'index.php?title={0.raw_title}&stableid={0.stable_id}'.format(self))

    @on_no_errors
    def compare_stable_and_current(self):
        latest_rev_id = list(self.wrapped_page.revisions())[0]['revid']
        print("TT", self.raw_title, latest_rev_id, self.stable_id)
        # import pdb; pdb.set_trace()
        if self.stable_id !=  latest_rev_id:
            self.errors.append(
                'The stable revision for "%s" is outdated' % self.raw_title)



    def find_stable_id(self):
        r = self.site.api("query", titles=self.raw_title, prop="flagged")
        pages = r['query']['pages']
        # pages is a dict with one key: the page_id we don't know yet.
        pid = list(pages.keys())[0]
        try:
            self.stable_id = int(pages[pid]['flagged']['stable_revid'])  # jay!
        except KeyError:
            self.errors.append(
                'No stable revision found for "%s"' % self.raw_title)

    def __str__(self):
        return "%s(%s)" % (self.raw_title, self.friendly_title)


class BaseBookTocItem(object):
    '''An item in a book toc'''

    def __init__(self, site, line):
        '''expects line to be a wikitext list item with a link'''
        self.is_valid = False
        self.errors = []
        try:
            self.parse_tocline(line)
        except AttributeError:
            self.errors.append("Can't parse toc-line: %s" % line)
            return
        self.target = self.link_parts[0].replace(" ", "_")
        if "#" in self.target:
            return
        self.text = self.link_parts[
            1 if len(self.link_parts) > 1 else 0].strip()
        self.is_valid = True
        self.stable_page = StablePage(site, self.title())
        self.errors += self.stable_page.errors

    def parse_tocline(self, line):
        match = re.match(self.item_re, line.strip())
        list_part, link_part = match.groups()
        self.depth = len(list_part)
        self.link_parts = link_part.split('|')

    def __str__(self):
        return str(self.__dict__)


class VersionizedBookTocItem(BaseBookTocItem):
    item_re = re.compile(r'((?:#|\*)+).*\[(.*)\]')
    title_re = re.compile(r'.*title=(.*?)&')

    def title(self):
        return re.match(self.title_re, self.target).groups()[0]


class LiveBookTocItem(BaseBookTocItem):
    item_re = re.compile(r'((?:#|\*)+).*\[\[(.*)\]\]')

    def title(self):
        return self.target


class Bookinfo(dict):
    def __getitem__(self, key):
        super().__getitem__(key.upper())

    def __setitem__(self, key, val):
        super().__setitem__(key.upper(), val)

    def validation_errors(self):
        errors = []
        if not "AUTOREN" in self or "HERAUSGEBER" in self:
            errors.append("AUTOREN oder HERAUSGEBER notwendig")
        return errors


class ExistingBook(object):
    '''Holds data of an exisiting handbuch.io-`book`

       Attempts to analyze the toc and the first template
       on the book's start page
    '''

    def __init__(self, site, title, version):
        '''
        Args:
            site (Site): Mwclient site object
            title(str): Booktitle
            version(str): Book version
        '''
        self.site = site
        self.errors = []
        self.version = version
        # self.site_url = get_siteurl(site)
        if self.version != "live":
            title = "/".join((title, self.version))
        self.book_page = StablePage(site, title)
        self.errors += self.book_page.errors
        self.toc = []
        self.parse_toc()
        self.parse_info()

    @on_no_errors
    def parse_toc(self):
        soup = BeautifulSoup(self.book_page.text, 'html.parser')
        try:
            toctext = soup.find_all("div", class_="BookTOC")[0].text.strip()
        except IndexError:
            self.errors.append(
                'No toc found for book "%s"' % self.book_page.friendly_title)
            return
        BookTocItemClz = (
            LiveBookTocItem if self.version == "live"
            else VersionizedBookTocItem)
        # logging.debug("TOC: %s" % str(toctext))
        for line in toctext.split(os.linesep):
            if not line:
                continue

            item = BookTocItemClz(self.site, line)
            self.errors += item.errors
            if item.is_valid:
                self.toc.append(item)

    @on_no_errors
    def parse_template_text(self, txt):
        txt = txt[txt.find('|'):]
        data = Bookinfo()
        if not txt:
            return data

        while(True):
            next_ = txt.find('|')
            keyval = txt[:next_].split("=")
            txt = txt[next_ + 1:]
            if len(keyval) == 2:
                k, v = keyval
                data[k.strip()] = v.strip()
            if next_ < 0:
                break

        return data

    @on_no_errors
    def parse_info(self):
        txt = self.book_page.text
        self.template_startpos = txt.find('{{')
        self.template_endpos = txt.find('}}') + 2
        inner = txt[self.template_startpos + 2: self.template_endpos - 2]
        d = self.parse_template_text(inner)
        if not d:
            self.errors.append(
                'No template found for "%s"' % self.book_page.friendly_title)
        self.info = d
        self.errors += self.info.validation_errors()

    @on_no_errors
    def get_pagetext_from_page(self, page):
        txt = "\n\n=%s=\n\n" % page.friendly_title.replace(self.book_page.friendly_title+"/", "")
        txt += page.text
        txt, numsubs = re.subn(
            "(=+\s*Einzelnachweise?\s*=+|<references\s*\/>)", "", txt)
        if numsubs > 0:
            self.found_references = True

        return txt

    @on_no_errors
    def get_src(self):
        self.found_references = False
        txt = ''
        for item in self.toc:
            if item.depth > 1:
                continue

            ptxt = self.get_pagetext_from_page(item.stable_page)
            txt += ptxt or ''

        if self.found_references:
            txt += "= Einzelnachweise =\n<references/>\n\n"

        return txt
