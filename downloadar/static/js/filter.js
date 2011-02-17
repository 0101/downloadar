;(function($){
    $.fn.entryFilter = function(options) {
        var opts = $.extend({}, $.fn.entryFilter.defaults, options);

        return this.each(function() {

            var self = $(this);
            var list = opts.list;
            var activeFeeds = {};

            function getActiveFeedList() {
                var list = [];
                for (var id in activeFeeds) {
                    list.push(id);
                }
                return list;
            }

            function createFeedButton(feed) {
                var button = $('<span/>', {class: 'switch', text: feed.name});
                feed.button = button;
                button.mousedown(function() {
                    if (button.is('.loading')) {
                        return;
                    }
                    if (button.is('.active')) {
                        deactivateFeed(feed);
                    } else {
                        activateFeed(feed);
                    }
                });
                return button;
            }

            function activateFeed(feed) {
                feed.button.addClass('loading');
                activeFeeds[feed.id] = true;

                list.trigger('fetch_select', [getActiveFeedList(), function() {
                    feed.button.removeClass('loading');
                    feed.button.addClass('active');
                }]);
                $.post(opts.urls.select, {'feed': feed.id});
                self.trigger('not_empty');
            }

            function deactivateFeed(feed) {
                delete activeFeeds[feed.id];
                list.trigger('fetch_unselect', [getActiveFeedList()]);
                feed.button.removeClass('active');
                $.post(opts.urls.unselect, {'feed': feed.id});
                if (getActiveFeedList().length == 0) {
                    self.trigger('empty');
                }
            }

            function filter(entry) {
                return (entry.feed in activeFeeds);
            }

            function filterEntries() {
                list.trigger('filter', [filter]);
            }

            function init() {
                $.each(opts.feeds, function(i, feed) {

                    self.append(createFeedButton(feed));

                    if (feed.selected) {
                        activeFeeds[feed.id] = true;
                        feed.button.addClass('active');
                    }
                });

                opts.status.trigger('start_loading_animation');
                opts.status.trigger('info', ['loading entries']);
                list.trigger('fetch_init', [getActiveFeedList(), function() {
                    opts.status.trigger('clear');
                }]);

                if (getActiveFeedList().length == 0) {
                    self.trigger('empty');
                } else {
                    self.trigger('not_empty');
                }
            }

            init();
        });
    }
    $.fn.entryFilter.defaults = {
        list: null,
        status: $(),
        feeds: []
    }
})(jQuery);
