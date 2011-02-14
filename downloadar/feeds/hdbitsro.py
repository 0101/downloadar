from django.conf import settings

from dlr import feed
from dlr.imdb import IMDBFeedMixin

class HdbitsFeed(IMDBFeedMixin, feed.BaseFeed):

    name = "HD-bits.ro"

    @property
    def url(self):
        return settings.HDBITSRO_URL


feed.register(HdbitsFeed)
