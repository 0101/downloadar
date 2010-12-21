import re
from hashlib import md5

from django.core.exceptions import ValidationError
from django.utils import simplejson as json

import feedparser

from dlr.models import Entry


__feed_registry = {}


def register(cls):
    __feed_registry[cls.get_id()] = cls()


def get(id):
    return __feed_registry[id]


def get_all():
    return __feed_registry.items()


def fetch_all(print_progress=False):
    for feed in __feed_registry.values():
        if print_progress:
            print 'Fetching %s...' % feed.name
        feed.fetch()


class BaseFeed(object):

    entry_model = Entry

    @property
    def name(self):
        return self.__class__.__name__

    @classmethod
    def get_id(cls):
        return cls.__name__

    def fetch(self):
        data = feedparser.parse(self.url)
        self.process_entries(data)

    def process_entries(self, data):
        map(self.store_entry, filter(self.filter_entry, data.entries))

    def filter_entry(self, entry_data):
        """
        return if given entry is supposed to be in this feed
        """
        return True

    def store_entry(self, entry_data):
        """
        Creates this feed's entry_model instance from feedparser entry data.

        Attempts to populate all fields of the model by calling
        self.get_entry_<field_name>.

        Validates the object and saves it if it's valid.
        """
        fields = [f.name for f in self.entry_model._meta.fields]
        default = lambda x: None
        entry = self.entry_model(**dict(
            [(f, getattr(self, 'get_entry_' + f, default)(entry_data))
                for f in fields]
        ))
        try:
            # TODO: special treatment of duplicate entries
            entry.full_clean()
        except ValidationError, e:
            # TODO: proper logging
            print "Entry didn't validate", self, e
            #print "data:\n", entry_data
        else:
            entry.save()

    def get_entry_uid(self, entry_data):
        dl_url = self.get_entry_download_url(entry_data)
        if not dl_url:
            raise NotImplementedError('%s must implement get_entry_uid '
                                      'method' % self.__class__.__name__)
        return md5(self.__class__.__name__ + dl_url).hexdigest()

    def get_entry_title(self, entry_data):
        try:
            return entry_data.title
        except AttributeError:
            raise NotImplementedError('%s must implement get_entry_title '
                                      'method' % self.__class__.__name__)

    def get_entry_download_url(self, entry_data):
        url = getattr(entry_data, 'link', None)
        return url.replace(' ', '%20') if url else None

    def get_entry_content_json(self, entry_data):
        summary = getattr(entry_data, 'summary', None)
        return json.dumps({'summary': summary}) if summary else None
