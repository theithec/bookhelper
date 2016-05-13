import random
import string
from datetime import datetime
from datacite import DataCiteMDSClient, schema31
from datacite.errors import DataCiteServerError


class BookDoi(object):

    def __init__(self, conf):
        self.errors = []
        # the book is always generated from the "live" version, so we need
        # the real version
        self.conf = conf
        #self.version = conf.dc_version

    def find_free_doi(self):

        r = "".join([random.choice( string.ascii_uppercase + string.digits)
                for _ in range(5)
            ])
        print("R", r)
        doi = "/".join([ self.conf.dc_identifier,r])
        print("DOI", doi)
        try:
            doc = self.client.metadata_get(doi)
            # self.errors.append('Doi "%s" already exists' % self.doi)
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
            'test_mode': True
        }
        self.client = DataCiteMDSClient(**self.datacite_kwargs)
        self.doi = self.find_free_doi()


    def _book_metadata(self):
        data = {
            'identifier': {
                'identifier': self.doi,
                'identifierType': 'DOI',
            },
            'creators': self.get_creators_list(),
            'titles': [
                {'title': self.book.book_page.friendly_title}
            ],
            'publisher': self.book.info['HERAUSGEBER'],
            'publicationYear': str(datetime.now().year),
            'version': str(self.version)
        }
        assert schema31.validate(data)
        return data

    def get_creators_list(self):
        creators = []
        for title in ['AUTOREN', 'KONTRIBUTOREN', ]:
            namesstr = self.book.info.get(title, "")
            dicts = [
                {'CreatorName': name.strip()}
                for name in namesstr.split(',')
                if name.strip()
            ]
            creators += [d for d in dicts if d]
            return creators
