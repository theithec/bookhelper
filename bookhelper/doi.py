from __future__ import absolute_import
from datetime import datetime
from datacite import DataCiteMDSClient, schema31
from datacite.errors import DataCiteServerError


class BookDoi(object):

    def __init__(self, conf):
        self.errors = []
        # the book is always generated from the "live" version, so we need
        # the real version
        self.conf = conf
        self.version = conf.dc_version

    def _bookdoi(self):
        return u'/'.join((
            self.datacite_kwargs[u'prefix'],
            self._versionized_identifier(),
        ))

    def _versionized_identifier(self):
        ident = u"{0.dc_identifier}/{0.dc_version}".format(self.conf)
        return ident

    def validate(self):
        self.datacite_kwargs = {
            u'username': self.conf.dc_symbol,
            u'password': self.conf.dc_password,
            u'prefix': self.conf.dc_prefix,
            u'test_mode': True
        }
        self.doi = self._bookdoi()
        self.client = DataCiteMDSClient(**self.datacite_kwargs)
        try:
            doc = self.client.metadata_get(self.doi)
            self.errors.append(u'Doi "%s" already exists' % self.doi)
        except DataCiteServerError, e:
            if e.error_code != 404:
                self.errors.append(
                    u'Not the expected result from MDS while validation: %s' % e)

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
