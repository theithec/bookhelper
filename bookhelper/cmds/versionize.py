'''
Creates a stable version of a book. That is, a page with a toc
containing stable links. Optionally creates dois.
'''
import os
from bs4 import BeautifulSoup

from bookhelper import ExistingBook, doihelper
from bookhelper.utils import get_siteurl, get_fullurl, on_no_errors
from . import SiteAction


class VersionizeAction(SiteAction):

    def versionize_pages(self):
        doistr = (
            '<span class="doi"><code>D.o.i.: [https://doi.org/{doi} {doi}]' +
            '</code></span>\n\n')
        for item in self.book.toc:
            cpage = self.site.Pages[item.target]
            try:
                rev_id = list(cpage.revisions())[0]['revid']
            except IndexError:
                # import pdb; pdb.set_trace()
                self.errors.append("No revison found for %s" % item.target)
                return
            self.site.api(
                revid=rev_id,
                flag_accuracy=2,
                action="review",
                token=self.site.get_token(type=None))
            item.stable_link = os.path.join(
                get_siteurl(self.site), 'w',
                'index.php?title=%s&stableid=%s' % (item.target, rev_id))
            soup = BeautifulSoup(cpage.text(), 'html.parser')
            olddoi = soup.find("span", class_="doi")
            if olddoi:
                olddoi.extract()
            if not self.conf.no_doi:
                doi = self.doihelper.create_chapterdoi(
                    item.stable_link,  item.text, self.book)
                print("\n\nDOI", doi)
                self.site.api(
                    action="setdoi",
                    doi=doi,
                    rev=str(rev_id),
                    token=self.site.get_token(type=None))

                ctxt = (
                    (doistr.format(doi=doi)) +
                    soup.decode(formatter=None).strip())
            cpage.save(ctxt)

    def versionized_template(self):
        if self.doihelper:
            self.book.info['doi'] = self.doihelper.create_bookdoi(
                self.vfullurl, self.book)
            self.book.info['version'] = self.conf.version
            self.book.info['title'] = self.book.book_page.friendly_title
            t = u"{{Bookinfo\n"
            info = dict([(k.upper(), v) for k, v in self.book.info.items()])
            for key in ['ABSTRACT', 'AUTOREN', 'HERAUSGEBER', 'KONTRIBUTOREN',
                        'STAND', 'DOI', 'VERSION', 'TITLE']:
                if key in info:
                    t += u"|%s = %s\n" % (key, info[key])
            t += "}}\n"

        return t


    @on_no_errors
    def versionize_bookpage_text(self):
        txt = self.book.book_page.text
        txt = (txt[:self.book.template_startpos] +
               self.versionized_template() +
               txt[self.book.template_endpos:])
        soup = BeautifulSoup(txt, 'html.parser')
        toc = soup.find('div', class_='BookTOC')
        content = toc.contents[0]
        stable_content = os.linesep
        fstr = '{depth} <span class="plainlinks">[{url} {text}]</span>\n'
        #import pdb; pdb.set_trace()
        for item in self.book.toc:
            print ("ITEM", item)
            stable_item = fstr.format(
                depth="#"*item.depth,
                url=item.stable_link,
                text = item.text)
            stable_content += stable_item

        content.replaceWith(stable_content)
        txt =  soup.decode(formatter=None)
        self.vbookpage.save(txt)

    @on_no_errors
    def versionize(self):
        self.vpagetitle = (
            '{0.book.book_page.raw_title}/{0.conf.version}'.format(self))
        self.vbookpage = self.site.Pages[self.vpagetitle]
        if self.vbookpage.text() and not self.conf.force_overwrite:
            self.errors.append("Page already exists")

        self.vfullurl = get_fullurl(self.site, self.vpagetitle)
        self.versionize_pages()
        self.versionize_bookpage_text()

    def run(self):
        self.doihelper = None
        if not self.conf.no_doi:
            self.doihelper = doihelper.DoiHelper(self.conf, self.errors)

        self.book = ExistingBook(self.site, self.conf.book, "live")
        self.errors += self.book.errors
        self.versionize()
