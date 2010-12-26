from datetime import datetime
import os
import re

from django.conf import settings
from django.contrib.auth.models import User
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
    feed = models.CharField(max_length=50)
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

    def clean(self):
        if not self.id:
            self.fetched = datetime.now()

    def get_template(self):
        return '%s/entry.html' % self.feed, 'entry.html'

    def render_to_html(self):
        context = json.loads(self.content_json, encoding='utf-8')
        context['entry'] = self
        return render_to_string(self.get_template(), context)

    def serialize(self):
        return {
            'id': self.id,
            'feed': self.feed,
            'title': self.title,
            'html': self.render_to_html(),
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
