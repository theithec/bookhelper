from __future__ import absolute_import
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

        r = u"".join([random.choice( string.ascii_uppercase + string.digits)
                for _ in xrange(5)
            ])
        doi = u"/".join([ self.conf.dc_identifier,r])
        try:
            doc = self.client.metadata_get(doi)
            # self.errors.append('Doi "%s" already exists' % self.doi)
            return self.find_free_doi()
        except DataCiteServerError, e:
            if e.error_code != 404:
                self.errors.append(
                    u'Not the expected result from MDS while validation: %s' % e)
        return doi



    def validate(self):
        self.datacite_kwargs = {
            u'username': self.conf.dc_symbol,
            u'password': self.conf.dc_password,
            u'prefix': self.conf.dc_prefix,
            u'test_mode': True
        }
        self.client = DataCiteMDSClient(**self.datacite_kwargs)
        self.doi = self.find_free_doi()


    def _book_metadata(self):
        data = {
            u'identifier': {
                u'identifier': self.doi,
                u'identifierType': u'DOI',
            },
            u'creators': self.get_creators_list(),
            u'titles': [
                {u'title': self.book.book_page.friendly_title}
            ],
            u'publisher': self.book.info[u'HERAUSGEBER'],
            u'publicationYear': unicode(datetime.now().year),
            u'version': unicode(self.version)
        }
        assert schema31.validate(data)
        return data

    def get_creators_list(self):
        creators = []
        for title in [u'AUTOREN', u'KONTRIBUTOREN', ]:
            namesstr = self.book.info.get(title, u"")
            dicts = [
                {u'CreatorName': name.strip()}
                for name in namesstr.split(u',')
                if name.strip()
            ]
            creators += [d for d in dicts if d]
            return creators
