import os
import re
from bs4 import BeautifulSoup
from .utils import get_siteurl, on_no_errors


EXPORTKEYS = ['odt', 'pdf', 'epub']


class StablePage(object):
    '''A wrapper around mwclients `Page`
       One revesion of every (book)-page should be marked as stable.
       And that revission is to be be used for generating documents/versions.
       However, it's a little bit complicate to receive the stable revision
       via the api. This is what we do here'''

    def __init__(self, site, title):
        self.errors = []
        self.raw_title = title
        self.friendly_title = title.replace("_", " ")
        _wrapped_page = site.Pages[title]
        if not _wrapped_page.text():
            self.errors.append(
                'No Page with this title was found: "%s"' % self.title)
            return
        r = site.api("query", titles=title, prop="flagged")
        pages = r['query']['pages']
        # pages is a dict with one key: the page_id we don't know yet.
        pid = list(pages.keys())[0]
        try:
            self.stable_id = int(pages[pid]['flagged']['stable_revid'])  # jay!
        except KeyError:
            self.errors.append('No stable revision found for "%s"' % title)
            return
        stable_rev = _wrapped_page.revisions(
            startid=self.stable_id,
            endid=self.stable_id,
            expandtemplates=False,
            prop="content")
        self.text = list(stable_rev)[0]['*']
        site_url = get_siteurl(site)
        self.fullurl = os.path.join(
            site_url, 'w',
            'index.php?title={0.raw_title}&stableid={0.stable_id}'.format(self))


class BaseBookTocItem(object):
    '''An item in a book toc'''

    def __init__(self, line):
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
        # self.page = StablePage(site, self._title())
        self.is_valid = True

    def parse_tocline(self, line):
        match = re.match(self.item_re, line.strip())
        # logging.debug("MATCH %s %s " % (line, str(match)))
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
    pass
    def __get__(self, key):
        #print("GET", key)
        super().__get__(key.upper())

    def __set__(self, key, val):
        #print("SET", key)
        super().__set__(key.upper(), val)

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
        #import pdb; pdb.set_trace()
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

            item = BookTocItemClz(line)
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
        else:
            #if not any(map(lambda k: d.get(k, None), ["AUTOREN"
            pass
        self.info = d
        self.errors += self.info.validation_errors()


    def get_pagetext_from_item(self, item):
        page = StablePage(self.site, item.title())
        txt = "\n\n=%s=\n\n" % page.friendly_title
        txt += page.text
        txt, numsubs = re.subn(
            "(=+\s*Einzelnachweise?\s*=+|<references\s*\/>)", "", txt)
        if numsubs > 0:
            self.found_references = True

        return txt

    def get_src(self):
        self.found_references = False
        txt = ''
        for item in self.toc:
            if item.depth > 1:
                continue
            ptxt = self.get_pagetext_from_item(item)
            txt += ptxt

        if self.found_references:
            txt += "= Einzelnachweise =\n<references/>\n\n"

        return txt
