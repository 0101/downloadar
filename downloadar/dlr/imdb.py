from os.path import join
import re
import urllib2

from django.conf import settings
from django.utils import simplejson as json

from dlr.models import Entry


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
        url = self.URL % {'id': id, 'title': title, 'year': year}
        response = urllib2.urlopen(url)
        if response.code == 200:
            data = json.loads(response.read(), encoding='utf-8')
            print data
            if data['Response'] == 'True':
                print 'returning'
                return data

IMDB = _ImdbAPI()


class IMDBFeedMixin(object):

    def _get_summary(self, entry_data):
        return getattr(entry_data, 'summary', None)

    def _update_entry_imdb_info(self, entry):
        try:
            id=entry.content['imdb']['id']
        except KeyError:
            return

        old_data = entry.content['imdb']
        imdb_data = IMDB.get(id=id)
        if not imdb_data:
            return

        # update title
        entry.title = imdb_data.get('Title') or entry.title

        # download a poster if we don't have it already
        poster_url = imdb_data.get('Poster')
        if (poster_url and (not entry.content.get('image') or
                            poster_url != old_data['Poster'])):

            try:
                response = urllib2.urlopen(poster_url)
            except ValueError:
                # probably wrong url in data e.g. "N/A"
                pass
            else:
                if response.code == 200:
                    # TODO: need to worry about different formats?
                    filename = '%s.jpg' % id
                    file_path = join(settings.IMAGE_DIR, 'imdb', filename)
                    f = open(file_path, 'wb+')
                    f.write(response.read())
                    f.close()
                    image_url = '%s/imdb/%s' % (settings.IMAGE_DIR_NAME, filename)
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
                    'id': find_imdb_id(link),
                }
                self._update_entry_imdb_info(entry)

