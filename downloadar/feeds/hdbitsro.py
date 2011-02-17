from datetime import datetime
from os.path import join
import re

from django.conf import settings

from BeautifulSoup import BeautifulSoup

from dlr import feed
from dlr.imdb import IMDBFeedMixin
from dlr.utils import download_image


IMAGE_RE = re.compile(r'src=')
TITLE_RE = re.compile(r'^(?P<title>.*) (?P<year>\d{4}) .*(?P<quality>720p|1080p)')


class HdbitsFeed(IMDBFeedMixin, feed.BaseFeed):

    name = "HD-bits.ro"

    @property
    def url(self):
        return settings.HDBITSRO_URL

    def get_entry_title(self, entry_data):
        try:
            return entry_data.title
        except AttributeError:
            #TODO: logging
            return '<No title>'

    def _get_image_from_summary(self, entry):
        """
        Downloads first image from summary and sets it as entry.content.image
        """
        summary = entry.content.get('summary')
        if summary:
            bs = BeautifulSoup(summary)
            img = bs.find('img')
            if img:
                src = img.get('src')
                if src:
                    ext = src.split('.')[-1]
                    if 3 <= len(ext) <= 4:
                        filename = '%s.%s' % (entry.uid, ext)
                        image_url = download_image(src, join('cache', filename))
                        if image_url:
                            entry.content['image'] = image_url
                            # replace original image src so it loads faster
                            img['src'] = settings.STATIC_URL + image_url
                            entry.content['summary'] = unicode(bs)

    def entry_pre_save(self, entry, entry_data):

        match = TITLE_RE.match(entry.title)
        if match:
            year = int(match.group('year'))
            if 1920 < year < (datetime.now().year + 1):
                # year seems legit... (still could have been part of the title tho)
                entry.title = match.group('title')
                entry.content['year'] = year
                entry.content['quality'] = match.group('quality')

        super(HdbitsFeed, self).entry_pre_save(entry, entry_data)

        # If we didn't get a poster from IMDB, pick first image from summary.
        if not entry.content.get('image'):
            self._get_image_from_summary(entry)
        entry.content['release_name'] = entry_data.title

    #def _update_images(self):
    #    from dlr.models import Entry
    #    for entry in Entry.objects.filter(feed_id=self.__class__.get_id()):
    #        if not entry.content.get('image'):
    #            self._get_image_from_summary(entry)
    #            entry.save()



feed.register(HdbitsFeed)
