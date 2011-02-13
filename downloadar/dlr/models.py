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


class EntryManager(models.Manager):
    def newest(self):
        return self.get_query_set().order_by('-id')


class Entry(models.Model):
    uid = models.CharField(max_length=200, unique=True)
    feed_id = models.CharField(max_length=50)
    title = models.CharField(max_length=200)
    download_url = models.URLField(null=True, blank=True, verify_exists=False)
    content_json = models.TextField(null=True, blank=True)
    fetched = models.DateTimeField(null=True, blank=True)
    downloaded = models.DateTimeField(null=True, blank=True)
    downloaded_by = models.ForeignKey(User, null=True, blank=True)

    objects = EntryManager()

    class Meta:
        verbose_name = _(u'Entry')
        verbose_name_plural = _(u'Entries')

    def __unicode__(self):
        return self.title

    @property
    def content(self):
        return json.loads(self.content_json, encoding='utf-8')

    @property
    def feed(self):
        from dlr import feed
        return feed.get(self.feed_id)

    @property
    def feed_name(self):
        return self.feed.name

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
        return '%s/entry.html' % self.feed_id, 'entry.html'

    def get_detail_template(self):
        return '%s/entry_detail.html' % self.feed_id, 'entry_detail.html'

    def render_to_html(self):
        context = self.content
        context['entry'] = self
        return render_to_string(self.get_template(), context)

    def serialize(self):
        return {
            'id': self.id,
            'feed': self.feed_id,
            'title': self.title,
            'html': self.render_to_html(),
            'url': reverse('dlr:get_entry', kwargs={'entry_id': self.id}),
            'detail_url': reverse('dlr:entry_detail', kwargs={'entry_id': self.id}),
        }


class UserProfile(JsonStore):
    user = models.ForeignKey(User, unique=True)

    def __unicode__(self):
        return u"%s's profile" % self.user.username


def create_profile(sender, created, instance=None, **kwargs):
    if created and instance:
        UserProfile.objects.create(user=instance)

post_save.connect(create_profile, sender=User)


# load feeds
files = [f for f in os.listdir(os.path.join(settings.PROJECT_DIR, 'feeds'))
         if re.match(r'^[^_]+.*\.py$', f)]
__import__('feeds', globals(), {}, [re.sub(r'\.py$', '', f) for f in files])
