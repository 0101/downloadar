from datetime import datetime
import os
import re

from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.fields import FieldDoesNotExist
from django.db.models.signals import post_save
from django.template.loader import render_to_string
from django.utils import simplejson as json
from django.utils.translation import ugettext_lazy as _

from jsonstore.models import JsonStore

from dlr.utils import JSONField, cached


class EntryManager(models.Manager):
    def newest(self):
        return self.get_query_set().order_by('-id')


class Entry(models.Model):
    uid = models.CharField(max_length=200, unique=True)
    feed_id = models.CharField(max_length=50)
    title = models.CharField(max_length=200)
    download_url = models.URLField(null=True, blank=True, verify_exists=False)
    content = JSONField(null=True, blank=True)
    fetched = models.DateTimeField(null=True, blank=True)
    downloaded = models.DateTimeField(null=True, blank=True)
    downloaded_by = models.ForeignKey(User, null=True, blank=True)
    imdb_id = models.CharField(max_length=16, null=True, blank=True, db_index=True)

    objects = EntryManager()

    class Meta:
        verbose_name = _(u'Entry')
        verbose_name_plural = _(u'Entries')

    def __unicode__(self):
        return self.title

    @property
    def feed(self):
        from dlr import feed
        return feed.get(self.feed_id)

    @property
    def feed_name(self):
        return self.feed.name

    @property
    def detail_url(self):
        return reverse('dlr:entry_detail', kwargs={'entry_id': self.id})

    @property
    @cached
    def other_releases(self):
        if self.imdb_id:
            entries = (Entry.objects.filter(imdb_id=self.imdb_id)
                       .exclude(id=self.id))
            if entries:
                return {
                    'available': filter(lambda e: not e.downloaded, entries),
                    'downloaded': filter(lambda e: e.downloaded, entries),
                }

    def clean(self):
        if not self.id:
            self.fetched = datetime.now()

    def download(self, user):
        assert not self.downloaded
        success, message = self.feed.download_torrent(self)
        if success:
            self.downloaded = datetime.now()
            self.downloaded_by = user
            self.save()
        return success, message

    def get_template(self):
        return self.feed.entry_template, 'entry.html'

    def get_detail_template(self):
        return self.feed.entry_detail_template, 'entry_detail.html'

    def render_to_html(self):
        context = self.content
        context['entry'] = self
        context['STATIC_URL'] = settings.STATIC_URL
        return render_to_string(self.get_template(), context)

    def serialize(self):
        return {
            'id': self.id,
            'feed': self.feed_id,
            'title': self.title,
            'html': self.render_to_html(),
            'url': reverse('dlr:get_entry', kwargs={'entry_id': self.id}),
            'detail_url': self.detail_url,
        }


class UserProfile(JsonStore):
    user = models.ForeignKey(User, unique=True)
    can_download = models.BooleanField(default=True)

    def __unicode__(self):
        return u"%s's profile" % self.user.username

    def save(self, *args, **kwargs):
        self.selected_feeds = self.selected_feeds or {}
        super(UserProfile, self).save(*args, **kwargs)


def create_profile(sender, created, instance=None, **kwargs):
    if created and instance:
        UserProfile.objects.create(user=instance)

post_save.connect(create_profile, sender=User)


# load feeds
files = [f for f in os.listdir(os.path.join(settings.PROJECT_DIR, 'feeds'))
         if re.match(r'^[^_]+.*\.py$', f)]
__import__('feeds', globals(), {}, [re.sub(r'\.py$', '', f) for f in files])
