from datetime import datetime
import os
import re

from django.conf import settings
from django.db import models
from django.utils import simplejson as json
from django.utils.translation import ugettext_lazy as _


class Entry(models.Model):
    uid = models.CharField(max_length=200, unique=True)
    title = models.CharField(max_length=200)
    download_url = models.URLField(null=True, blank=True, verify_exists=False)
    content_json = models.TextField(null=True, blank=True)
    fetched = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _(u'Entry')
        verbose_name_plural = _(u'Entries')

    def __unicode__(self):
        return self.title

    def clean(self):
        if not self.id:
            self.fetched = datetime.now()


# load feeds
files = [f for f in os.listdir(os.path.join(settings.PROJECT_DIR, 'feeds'))
         if re.match(r'^[^_]+.*\.py$', f)]
__import__('feeds', globals(), {}, [re.sub(r'\.py$', '', f) for f in files])
