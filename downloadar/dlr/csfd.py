import re
from django.utils.http import urlquote_plus
import urllib2

from BeautifulSoup import BeautifulSoup

from dlr.models import Entry


SEARCH_URL = u'http://www.csfd.cz/hledat/?q=%s'


def get_film(title=None, imdb_id=None, url=None):
    """
    Tries to find film profile on CSFD. If successful, returns dictionary of
    parsed data, otherwise None.

    Either film's CSFD profile URL, or title and IMDB ID is required.

    {
        'link': url of csfd profile,
        'rating': csfd rating as integer 0-100,
        'votes': vote count,
    }
    """

    film = _fetch_film(url) if url else _find_film(title, imdb_id)
    if not film:
        return

    url, page = film

    return {
        'link': url,
        'rating': _get_rating(page),
        'votes': _get_votes(page),
    }


def _find_film(title, imdb_id):
    """
    Tries to find film profile on CSFD. If successful, returns tuple
    (csfd profile url, BeautifulSoup of the page), otherwise None
    """
    search_url = SEARCH_URL % urlquote_plus(title)
    search_results = BeautifulSoup(urllib2.urlopen(search_url))
    films_found = search_results.find(attrs={'id': 'search-films'})
    if not films_found:
        return

    links = films_found.findAll('a', 'film')
    if not links:
        return

    for link in links:
        href = link.get('href')
        if not href:
            continue
        url = 'http://www.csfd.cz' + href
        try:
            profile_page = BeautifulSoup(urllib2.urlopen(url))
        except Exception, e:
            # TODO: logging
            print 'csfd parsing error: ', e
            continue

        imdb_link = profile_page.find('a', 'imdb')
        if not imdb_link:
            continue

        if imdb_id in imdb_link.get('href', ''):
            return url, profile_page


def _fetch_film(url):
    try:
        return url, BeautifulSoup(urllib2.urlopen(url))
    except Exception, e:
        # TODO logging
        print 'csfd _fetch_film error: ', e


def _get_rating(page, url=None):
    try:
        rating_string = (page.find(attrs={'id': 'rating'})
                         .find(attrs={'class': 'average'}).text)
    except AttributeError:
        # TODO logging
        print 'csfd _get_rating parsing error @ ', url
        return
    rating = re.sub('[^\d]+', '', rating_string)
    try:
        value = int(rating)
        if 0 <= value <= 100:
            return value
        # TODO logging
        print 'csfd parsing error @ ', url, value
    except ValueError:
        # TODO logging
        print 'csfd parsing error @ ', url, rating_string


def _get_votes(page, url=None):
    rating_count_element = page.find(attrs={'id': 'rating-count-link'})
    if rating_count_element:
        return re.sub('[^\d]+', '', rating_count_element.text)
    # TODO logging
    print 'csfd _get_votes parsing error @ ', url


class CSFDFeedMixin(object):
    """
    Adds CSFD info to entries, assumes IMDB info is already present
    """
    def _update_entry_csfd_info(self, entry):
        try:
            url = entry.content['csfd']['link']
        except KeyError:
            try:
                imdb_id = entry.content['imdb']['ID']
            except KeyError:
                return
            new_data = get_film(title=entry.title, imdb_id=imdb_id)
        else:
            new_data = get_film(url=url)
        if not new_data:
            return

        if 'csfd' not in entry.content:
            entry.content['csfd'] = {}

        for key, val in new_data.items():
            if val is not None:
                entry.content['csfd'][key] = val

    def _csfd_update_all(self):
        for e in Entry.objects.filter(feed_id=self.__class__.get_id()):
            self._update_entry_csfd_info(e)
            e.save()

    def entry_pre_save(self, entry, entry_data):
        super(CSFDFeedMixin, self).entry_pre_save(entry, entry_data)
        self._update_entry_csfd_info(entry)
