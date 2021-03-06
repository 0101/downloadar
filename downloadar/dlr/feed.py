from hashlib import md5
import re
from urllib2 import urlopen

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import simplejson as json
from django.utils._os import safe_join

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
    entry_template = 'entry.html'
    entry_detail_template = 'entry_detail.html'

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
        Return if given entry is supposed to be in this feed.
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
        entry.feed_id = self.__class__.get_id()

        try:
            entry.full_clean()
        except ValidationError, e:
            # TODO: proper logging
            if not 'uid' in e.message_dict:
                print "%s: entry %s didn't validate: %s" % (
                    self.name, getattr(entry, 'title', ''), e
                )
        else:
            self.entry_pre_save(entry, entry_data)
            # TODO: validate again?
            entry.save()
            print '%s: added [%s] %s' % (self.name, entry.id, entry.title)

    def download_torrent(self, entry):
        """
        Download a .torrent file from the tracker and store it in
        settings.TORRENT_DOWNLOAD_DIR

        returns tuple (success, message)
        """
        if not entry.download_url:
            return False, 'This entry has no download URL'

        code, data, filename = self.fetch_torrent(entry)

        if code == 200:
            path = safe_join(settings.TORRENT_DOWNLOAD_DIR, filename)
            f = open(path, 'w+b')
            f.write(data)
            f.close()
            return True, u'%s downloaded' % filename
        else:
            return False, u'Error %s' % code

    def fetch_torrent(self, entry):
        """
        Download the .torrent file from the tracker. This should return
        a (HTTP status code, data, filename) tuple.
        """
        #from time import sleep; sleep(1)
        #return 200, 'lol', entry.download_url.split('/')[-1]
        response = urlopen(entry.download_url)
        filename = entry.download_url.split('/')[-1]
        return response.code, response.read(), filename

    def get_entry_uid(self, entry_data):
        """
        Return a unique identifier for the entry. Used to avoid duplicates.
        """
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

    def get_entry_content(self, entry_data):
        return '{}'

    def entry_pre_save(self, entry, entry_data):
        """
        Hook to do something with the entry object before it's saved.
        """
        summary = getattr(entry_data, 'summary', None)
        if summary is not None:
            entry.content['summary'] = summary
