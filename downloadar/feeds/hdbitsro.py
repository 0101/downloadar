from django.conf import settings

from dlr import feed


class HdbitsFeed(feed.BaseFeed):

    name = "HD-bits.ro"

    @property
    def url(self):
        return settings.HDBITSRO_URL


feed.register(HdbitsFeed)
