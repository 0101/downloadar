from os.path import join
import re
import urllib
import urllib2

from django.conf import settings
from django.utils import simplejson as json

from dlr.models import Entry
from dlr.utils import download_image


IMDB_LINK_RE = re.compile(r'http://(www\.)?imdb\.com/title/(tt\d+)')


def find_imdb_link(source):
    """
    Tries to find an imdb link in supplied string. Returns first found link
    or None.
    """
    match = IMDB_LINK_RE.search(source)
    return match.group() if match else None


def find_imdb_id(source):
    """
    Tries to find an imdb link in supplied string. Returns imdb ID from first
    found link or None.
    """
    match = IMDB_LINK_RE.search(source)
    return match.group(2) if match else None


class _ImdbAPI(object):

    URL = 'http://www.imdbapi.com/?i=%(id)s&t=%(title)s&y=%(year)s'

    def get(self, id='', title='', year=''):
        url = self.URL % {
            'id': id,
            'title': urllib.quote_plus(title),
            'year': year,
        }
        response = urllib2.urlopen(url)
        if response.code == 200:
            data = json.loads(response.read(), encoding='utf-8')
            if data['Response'] == 'True':
                return data

    def get_link(self, id):
        return 'http://www.imdb.com/title/%s' % id

IMDB = _ImdbAPI()


class IMDBFeedMixin(object):

    entry_template = 'movies/entry.html'
    entry_detail_template = 'movies/entry_detail.html'

    def _get_summary(self, entry_data):
        return getattr(entry_data, 'summary', None)

    def _update_entry_imdb_info(self, entry, data=None):
        try:
            id=entry.content['imdb']['ID']
        except KeyError:
            return

        entry.imdb_id = id

        old_data = entry.content['imdb']
        imdb_data = data or IMDB.get(id=id)
        if not imdb_data:
            return

        # update title
        title = imdb_data.get('Title')
        if title:
            if entry.title:
                entry.content['release_name'] = entry.title
            entry.title = title

        # download a poster if we don't have it already
        poster_url = imdb_data.get('Poster')
        if (poster_url and (not entry.content.get('image') or
                            poster_url != old_data['Poster'])):

            # TODO: need to worry about different formats?
            filename = '%s.jpg' % id
            image_url = download_image(poster_url, join('imdb', filename))
            if image_url:
                entry.content['image'] = image_url

        entry.content['imdb'].update(imdb_data)

    def _imdb_update_all(self):
        for e in Entry.objects.filter(feed_id=self.__class__.get_id()):
            self._update_entry_imdb_info(e)
            e.save()

    def entry_pre_save(self, entry, entry_data):
        super(IMDBFeedMixin, self).entry_pre_save(entry, entry_data)
        summary = self._get_summary(entry_data)
        if summary:
            link = find_imdb_link(summary)
            if link:
                entry.content['imdb'] = {
                    'link': link,
                    'ID': find_imdb_id(link),
                }
                self._update_entry_imdb_info(entry)
                return
        # if there's no link, try to find the entry by title & year
        title = entry.title
        year = entry.content.get('year')
        if title and year:
            data = IMDB.get(title=title, year=year)
            if int(data.get('Year', -1)) == year:
                entry.content['imdb'] = data
                entry.content['imdb']['link'] = IMDB.get_link(data.get('ID'))
                self._update_entry_imdb_info(entry, data)
