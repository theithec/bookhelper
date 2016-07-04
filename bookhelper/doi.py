import random
import string
from datetime import datetime
from jsonschema.exceptions import ValidationError
from datacite import DataCiteMDSClient, schema31
from datacite.errors import DataCiteServerError


class BookDoi(object):

    test_mode = False

    def __init__(self, conf, book):
        self.errors = []
        self.conf = conf
        self.book = book

    def find_free_doi(self):
        r = "".join([random.choice(string.ascii_uppercase + string.digits)
                    for _ in range(5)])
        doi = "/".join([self.conf.dc_prefix, self.conf.dc_identifier, r])
        try:
            self.client.metadata_get(doi)
            #  self.errors.append('Doi "%s" already exists' % self.doi)
            return self.find_free_doi()
        except DataCiteServerError as e:
            if e.error_code != 404:
                self.errors.append(
                    'Not the expected result from MDS while validation: %s' % e)
        return doi

    def validate(self):
        self.datacite_kwargs = {
            'username': self.conf.dc_symbol,
            'password': self.conf.dc_password,
            'prefix': self.conf.dc_prefix,
            'test_mode': self.test_mode
        }
        self.client = DataCiteMDSClient(**self.datacite_kwargs)
        self.doi = self.find_free_doi()

    def get_book_metadata(self):
        publisher = self.book.info.get('HERAUSGEBER', None) or \
                self.book.info['AUTOREN']
        data = {
            'identifier': {
                'identifier': self.doi,
                'identifierType': 'DOI',
            },
            'creators': self.get_creators_list(),
            'titles': [
                {'title': self.book.book_page.friendly_title}
            ],
            'publisher': publisher,
            'publicationYear': str(datetime.now().year),
            'version': str(self.conf.version)
        }
        try:
            schema31.validate(data)
        except ValidationError as e:
            self.errors.append(str(e))
        return data

    def get_creators_list(self):
        creators = []
        for title in ['AUTOREN', 'HERAUSGEBER', 'KONTRIBUTOREN', ]:
            namesstr = self.book.info.get(title, "")
            dicts = [
                {'creatorName': name.strip()}
                for name in namesstr.split(',')
                if name.strip()
            ]
            creators += [d for d in dicts if d]

        return creators

    def set_doi(self, url, doi, datacite_kwargs):
        self.doi = doi
        data = self.get_book_metadata()
        try:
            doc = schema31.tostring(data)
        except DataCiteServerError as e:
                self.errors.append(e)
        client = DataCiteMDSClient(**datacite_kwargs)
        res = client.metadata_post(doc)
        if not res.startswith("OK"):
            self.errors.append(res)
            return
        for testurl in [
            "https://test.osl.tib.eu",
            "https://develop.osl.tib.eu",
            "https://handbuch.local",

        ]:
            if testurl in url:
                url = url.replace(testurl, "http://handbuch.io")

        if  "handbuch.io" in url and not self.test_mode:

            client.doi_post(doi, url)
