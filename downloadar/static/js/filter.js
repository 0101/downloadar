;(function($){
    $.fn.entryFilter = function(options) {
        var opts = $.extend({}, $.fn.entryFilter.defaults, options);

        return this.each(function() {

            var self = $(this);
            var list = opts.list;
            var activeFeeds = {};

            function createFeedButton(feed) {
                var button = $('<span/>', {class: 'button', text: feed.name});
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
                list.trigger('load_merge', [[feed.id], function() {
                    filterEntries();
                    feed.button.removeClass('loading');
                    feed.button.addClass('active');
                }]);
                $.post(opts.urls.select, {'feed': feed.id});
            }

            function deactivateFeed(feed) {
                delete activeFeeds[feed.id];
                filterEntries();
                feed.button.removeClass('active');
                $.post(opts.urls.unselect, {'feed': feed.id});
            }

            function filter(entry) {
                return (entry.feed in activeFeeds);
            }

            function filterEntries() {
                //console.log(activeFeeds);
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

                activeFeedList = [];
                for (var id in activeFeeds) {
                    activeFeedList.push(id);
                }
                list.trigger('load_append', [activeFeedList]);
            }

            init();
        });
    }
    $.fn.entryFilter.defaults = {
        list: null,
        feeds: []
    }
})(jQuery);
