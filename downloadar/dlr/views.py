from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils import simplejson as json
from django.views.generic.base import View
from django.views.generic.simple import direct_to_template

from dlr.models import Entry
from dlr import feed


class JSONResponseMixin(object):
    def render_to_response(self, content):
        serialized_content = json.dumps(content, ensure_ascii=False)
        return HttpResponse(serialized_content, content_type='application/json')


def index(request, template='index.html'):
    selected = request.user.get_profile().get('selected_feeds') or {}
    feeds = [{'id': id, 'name': f.name, 'selected': id in selected}
             for id, f in feed.get_all()]
    feeds = json.dumps(feeds, ensure_ascii=False)
    return direct_to_template(request, template, {'feeds': feeds})


class Entries(JSONResponseMixin, View):
    def get(self, request):
        feeds = request.GET.getlist('feeds[]')
        limit = max(int(request.GET.get('limit', 0)), 15)
        gt = request.GET.get('gt')
        lt = request.GET.get('lt')
        entries = Entry.objects.newest().filter(feed_id__in=feeds)
        if gt:
            entries = entries.filter(id__gt=gt)
        if lt:
            entries = entries.filter(id__lt=lt)

        return self.render_to_response({
            'entries': [e.serialize() for e in entries[:limit]],
            'more': entries.count() > limit,
        })

class EntryListItem(JSONResponseMixin, View):
    def get(self, request, entry_id):
        entry = get_object_or_404(Entry, id=entry_id)
        return self.render_to_response({'entry': entry.serialize()})


def select(request):
    feed = request.POST.get('feed')
    if not request.method == 'POST' or not feed:
        return HttpResponseBadRequest()

    profile = request.user.get_profile()
    if feed not in profile.selected_feeds:
        profile.selected_feeds[feed] = True
        profile.save()

    return HttpResponse('ok')


def unselect(request):
    feed = request.POST.get('feed')
    if not request.method == 'POST' or not feed:
        return HttpResponseBadRequest()

    profile = request.user.get_profile()
    try:
        del profile.selected_feeds[feed]
    except KeyError:
        pass
    else:
        profile.save()

    return HttpResponse('ok')


def entry_detail(request, entry_id):
    entry = get_object_or_404(Entry, id=entry_id)
    template = entry.get_detail_template()
    context = {'entry': entry}
    return render_to_response(template, context,
                              context_instance=RequestContext(request))


class Download(JSONResponseMixin, View):
    def post(self, request):
        entry_id = request.POST.get('entry_id')
        if entry_id:
            entry = get_object_or_404(Entry, id=entry_id)
            if not entry.downloaded:
                success, message = entry.download(request.user)
                return self.render_to_response({
                    'status': 'ok' if success else 'error',
                    'message': message,
                    'html': render_to_string('includes/download_section.html',
                                             {'entry': entry})
                })
        return HttpResponseBadRequest()
