from django.core.management.base import NoArgsCommand

import dlr.models
from dlr import feed


class Command(NoArgsCommand):
    help = ('Fetch all the feeds and save new entries to DB. Probably '
            'a good idea to put this into cron.')

    def handle_noargs(self, **options):
        feed.fetch_all(print_progress=True)
        print 'done.'
