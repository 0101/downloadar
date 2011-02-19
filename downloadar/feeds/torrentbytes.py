from datetime import datetime
import re
import urllib2

from django.conf import settings

from dlr import feed
from dlr.csfd import CSFDFeedMixin
from dlr.imdb import IMDBFeedMixin


TITLE_RE = re.compile(r'^(?P<title>.*)\.(?P<year>\d{4})\..*(?P<quality>720p|1080p)')


class TorrentBytesX264Feed(CSFDFeedMixin, IMDBFeedMixin, feed.BaseFeed):

    name = "TB Movies/x264"

    entry_detail_template = 'torrentbytes/entry_detail.html'

    @property
    def url(self):
        return settings.TORRENTBYTES_URL

    def fetch_torrent(self, entry):
        opener = urllib2.build_opener()
        opener.addheaders.append(('Cookie', 'uid=%(uid)s; pass=%(pass)s' % {
            'uid': settings.TORRENTBYTES_UID,
            'pass': settings.TORRENTBYTES_PASS,
        }))
        response = opener.open(entry.download_url)
        # TODO: recover from exceptions, logging
        filename = (response.info()['Content-Disposition']
                    .split('filename=')[-1].replace('"', ''))
        return response.code, response.read(), filename

    def filter_entry(self, entry_data):
        return entry_data.category == 'Movies/x264'

    def entry_pre_save(self, entry, entry_data):

        match = TITLE_RE.match(entry.title)
        if match:
            year = int(match.group('year'))
            if 1920 < year < (datetime.now().year + 1):
                # year seems legit... (still could have been part of the title tho)
                entry.title = match.group('title').replace('.', '')
                entry.content['year'] = year
                entry.content['quality'] = match.group('quality')

        super(TorrentBytesX264Feed, self).entry_pre_save(entry, entry_data)

        try:
            entry.content['release_name'] = entry_data.title.split(' ')[0]
        except Exception, ex:
            # TODO: logging
            print 'TorrentBytesX264Feed.entry_pre_save', ex


class TorrentBytesXvidFeed(TorrentBytesX264Feed):

    name = "TB Movies/Xvid"

    def filter_entry(self, entry_data):
        return entry_data.category == 'Movies/XviD'


feed.register(TorrentBytesX264Feed)
feed.register(TorrentBytesXvidFeed)
