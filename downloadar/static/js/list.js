;(function($){
    $.fn.entryList = function(options) {
        var opts = $.extend({}, $.fn.entryList.defaults, options);

        return this.each(function() {
            var self = $(this);
            var list = $('<ul/>').appendTo(self);
            var loadedFeeds = {};
            var entries = [];

            function fetchEntries(feedList, handler, callback) {
                callback = callback || function(){};

                var feeds = [];
                $.each(feedList, function(i, feed) {
                    if (!(feed in loadedFeeds)) {
                        feeds.push(feed);
                        loadedFeeds[feed] = true;
                    }
                });

                if (feeds.length == 0) {
                    callback();
                    return;
                }

                $.get(opts.urls.get_entries, {feeds: feeds}, function(response) {
                    handler(response.entries, callback);
                }, 'json');
            }

            function mergeEntries(newEntries, callback) {

                entries = entries.concat(newEntries);
                entries.sort(function(x, y){return y.id - x.id});

                //console.log($.map(entries, function(e){return e.id}));

                var prevElement = null;
                $.each(entries, function(i, entry) {
                    if (entry.element) {
                        prevElement = entry.element;
                    } else {
                        var e = createElement(entry);
                        entry.element = e;
                        if (prevElement) {
                            e.insertAfter(prevElement);
                        } else {
                            e.prependTo(list);
                        }
                        prevElement = e;
                    }
                });

                callback();
            }

            function addEntries(newEntries, addFn) {
                $.each(newEntries, function(i, entry) {
                    var e = createElement(entry);
                    entry.element = e;
                    addFn(e);
                });
            }

            function appendEntries(newEntries, callback) {
                addEntries(newEntries, function(entry) {list.append(entry)} );
                entries = entries.concat(newEntries);
            }

            function prependEntries(newEntries, callback) {
                addEntries(newEntries, function(entry) {list.prepend(entry)} );
                entries = newEntries.concat(entries);
            }

            function createElement(entry) {
                return $('<li/>').html(entry.html).data('id', entry.id);
            }

            function filter(fn) {
                $.each(entries, function(i, entry){

                    if (fn(entry)) {
                        //console.log('filtering entry:', entry.id, entry.title, 'result: show');
                        entry.element.show();
                    } else {
                        //console.log('filtering entry:', entry.id, entry.title, 'result: hide');
                        entry.element.hide();
                    }
                });
            }

            function init() {
                self.find('li').live('click', function() {
                    console.log($(this).data('id'));
                });
            }

            self.bind('load_merge', function(event, feedList, callback) {
                fetchEntries(feedList, mergeEntries, callback);
            });

            self.bind('load_append', function(event, feedList, callback) {
                fetchEntries(feedList, appendEntries, callback);
            });

            self.bind('load_prepend', function(event, feedList, callback) {
                fetchEntries(feedList, prependEntries, callback);
            });

            self.bind('filter', function(event, fn) {
                filter(fn);
            });

            init();
        });
    }
    $.fn.entryList.defaults = {}
})(jQuery);
