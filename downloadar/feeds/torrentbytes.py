from django.conf import settings

from dlr import feed


class TorrentBytesX264Feed(feed.BaseFeed):

    name = "TorrentBytes Movies/x264"

    @property
    def url(self):
        return settings.TORRENTBYTES_URL

    def fetch_torrent(self, entry):
        raise NotImplementedError('TODO: downloading from TorrentBytes')

    def filter_entry(self, entry_data):
        return entry_data.category == 'Movies/x264'


class TorrentBytesXvidFeed(TorrentBytesX264Feed):

    name = "TorrentBytes Movies/Xvid"

    def filter_entry(self, entry_data):
        return entry_data.category == 'Movies/XviD'


feed.register(TorrentBytesX264Feed)
feed.register(TorrentBytesXvidFeed)
