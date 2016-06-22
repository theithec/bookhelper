import random
import string
from datetime import datetime
from jsonschema.exceptions import ValidationError
from datacite import DataCiteMDSClient, schema31
from datacite.errors import DataCiteServerError


class BookDoi(object):

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
            'test_mode': False
        }
        self.client = DataCiteMDSClient(**self.datacite_kwargs)
        self.doi = self.find_free_doi()
        data = self.get_book_metadata()
        try:
            self.doc = schema31.tostring(data)
        except DataCiteServerError as e:
                self.errors.append(e)

    def get_book_metadata(self):
        print(self.book.info)
        data = {
            'identifier': {
                'identifier': self.doi,
                'identifierType': 'DOI',
            },
            'creators': self.get_creators_list(),
            'titles': [
                {'title': self.book.book_page.friendly_title}
            ],
            'publisher': self.book.info.get(
                'HERAUSGEBER', self.book.info['AUTOREN']),
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
        for title in ['AUTOREN', 'KONTRIBUTOREN', ]:
            namesstr = self.book.info.get(title, "")
            dicts = [
                {'creatorName': name.strip()}
                for name in namesstr.split(',')
                if name.strip()
            ]
            creators += [d for d in dicts if d]
            return creators

    def set_doi(self, url, doi, doc, datacite_kwargs):
        client = DataCiteMDSClient(**datacite_kwargs)
        res = client.metadata_post(doc)
        print(res)
        if not res.startswith("OK"):
            self.errors.append(res)
            return
        client.doi_post(doi, url)
