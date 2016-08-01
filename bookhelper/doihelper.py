import logging
import string
import random
from datetime import datetime
from jsonschema.exceptions import ValidationError
from datacite import DataCiteMDSClient, schema31
from datacite.errors import DataCiteServerError
from bookhelper.utils import on_no_errors


class DoiHelper(object):

    def __init__(self, conf, errors):
        self.conf = conf
        self.errors = errors
        self.test_mode = True
        self._create_client()

    @on_no_errors
    def _create_client(self):
        datacite_kwargs = {
            'username': self.conf.dc_symbol,
            'password': self.conf.dc_password,
            'prefix': self.conf.dc_prefix,
            'test_mode': self.test_mode}
        try:
            self.client = DataCiteMDSClient(**datacite_kwargs)
        except Exception as e:
            self.errors.append(str(e))

    @on_no_errors
    def find_free_doi(self):
        r = "".join([random.choice(string.ascii_uppercase + string.digits)
                     for _ in range(5)])
        doi = "/".join([self.conf.dc_prefix, self.conf.dc_identifier, r])
        try:
            self.client.metadata_get(doi)
            return self.find_free_doi()
        except DataCiteServerError as e:
            if e.error_code != 404:
                self.errors.append(
                    'Not the expected result from MDS while validation: %s' % e)

        return doi

    @on_no_errors
    def _post_metadata(self, metadata):
        logging.debug("METADATA:" + metadata)
        res = self.client.metadata_post(metadata)
        if not res.startswith("OK"):
            self.errors.append(res)

    @on_no_errors
    def _post_doi(self, doi, url):
        for testurl in [
            "https://test.osl.tib.eu",
            "https://develop.osl.tib.eu",
            "https://handbuch.local",

        ]:
            if testurl in url:
                url = url.replace(testurl, "http://handbuch.io")

        if "handbuch.io" in url and not self.test_mode:
            logging.debug("Post DOI: Doi: %s\t%s" % (self.doi, url))
            self.client.doi_post(self.doi, url)

    def _get_creators_list(self, book):
        creators = []
        for title in ['AUTOREN', 'HERAUSGEBER', 'KONTRIBUTOREN', ]:
            namesstr = book.info.get(title, "")
            dicts = [
                {'creatorName': name.strip()}
                for name in namesstr.split(',')
                if name.strip()
            ]
            creators += [d for d in dicts if d]

        return creators

    def _get_bookdata(self, book):
        publisher = book.info.get('HERAUSGEBER', None) or \
            book.info['AUTOREN']
        data = {
            'identifier': {
                'identifier': book.info['doi'],
                'identifierType': 'DOI',
            },
            'creators': self._get_creators_list(book),
            'titles': [
                {'title': book.book_page.friendly_title}
            ],
            'publisher': publisher,
            'publicationYear': str(datetime.now().year),
            'version': str(self.conf.version)
        }
        return data

    def _create_doi(self, doi, url, data):
        metadata = None
        try:
            schema31.validate(data)
            metadata = schema31.tostring(data)
        except ValidationError as e:
            self.errors.append(str(e))

        self._post_metadata(metadata)
        self._post_doi(doi, url)

    @on_no_errors
    def create_chapterdoi(self, doi, url, title, book):
        data = self._get_bookdata(book)
        data['titles'][0]['title'] = title
        data['relatedIdentifiers'] = [{
               'relatedIdentifier': book.info['doi'],
               'relatedIdentifierType': 'DOI',
               'relationType':'IsPartOf'}, ]
        self._create_doi(doi, url, data)

    @on_no_errors
    def create_bookdoi(self, url, book):
        data = self._get_bookdata(book)
        self._create_doi(book.info['doi'], url, data)
