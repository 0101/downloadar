from django.http import HttpResponse, HttpResponseBadRequest
from django.utils import simplejson as json
from django.views.generic.simple import direct_to_template

from dlr.models import Entry
from dlr import feed


def index(request, template='index.html'):
    selected = request.user.get_profile().get('selected_feeds') or {}
    feeds = [{'id': id, 'name': f.name, 'selected': id in selected}
             for id, f in feed.get_all()]
    feeds = json.dumps(feeds, ensure_ascii=False)
    return direct_to_template(request, template, {'feeds': feeds})


def get_entries(request):
    limit = 10
    feeds = request.GET.getlist('feeds[]')
    gt = request.GET.get('gt')
    entries = Entry.objects.newest().filter(feed__in=feeds)
    if gt:
        entries = entries.filter(id__gt=gt)

    response = {
        'entries': [e.serialize() for e in entries[:limit]],
        'more': entries.count() > limit,
    }
    json_string = json.dumps(response, ensure_ascii=False)
    return HttpResponse(json_string)


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
