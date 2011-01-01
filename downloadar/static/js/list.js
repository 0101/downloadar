;(function($){

    var doNothing = function() {};

    $.fn.entryList = function(options) {
        var opts = $.extend({}, $.fn.entryList.defaults, options);

        return this.each(function() {
            var self = $(this);
            var list = $('<ol/>').appendTo(self);
            var entries = [];
            var entryMap = {};
            var moreButton = null;
            var lastFeedList = [];
            var currentLimit = 0;
            var scrollable = opts.getScrollableParent(self);
            var separator = null;
            var detailPane = opts.detailPane;
            var activeEntry = null;

            var handlers = {
                pre: {
                    nothing: function(request) {
                        return request;
                    },
                    unselect: function(request) {
                        // set fixed height to prevent jumping
                        list.height(list.height());

                        request = handlers.pre.sendLimit(request);
                        var newEntries = [];
                        $.each(entries, function(index, entry) {
                            if ($.inArray(entry.feed, request.feeds) == -1) {
                                removeEntry(entry);
                            } else {
                                newEntries.push(entry);
                            }
                        });
                        entries = newEntries;
                        return request;
                    },
                    more: function(request) {
                        request.lt = entries[entries.length-1].id;
                        return request;
                    },
                    sendLimit: function(request) {
                        request.limit = entries.length;
                        return request;
                    }
                },
                post: {
                    append: function(newEntries, callback) {
                        $.each(newEntries, function(i, entry) {
                            entries.push(entry);
                            entryMap[entry.id] = entry;
                            var e = create.entryElement(entry);
                            entry.element = e;
                            e.appendTo(list);
                            e.fadeIn(opts.animationDelay);
                        });

                        callback();
                    },
                    merge: function(newEntries, callback) {
                        // set fixed height to prevent jumping
                        list.height(list.height());

                        $.each(newEntries, function(i, entry) {
                            if (entry.id in entryMap) {
                                return;
                            }
                            entries.push(entry);
                            entryMap[entry.id] = entry;
                        });

                        entries.sort(function(x, y){return y.id - x.id});

                        // remove old entries overflowing current limit
                        var diff = (entries.length - newEntries.length);
                        for (var i = 0; i < diff; i++) {
                            var entry = entries.pop();
                            removeEntry(entry);
                        }

                        var previous = null;

                        $.each(entries, function(i, entry) {
                            if (entry.element) {
                                previous = entry.element;
                                return;
                            }
                            var e = create.entryElement(entry);
                            entry.element = e;
                            if (previous) {
                                e.insertAfter(previous);
                            } else {
                                e.prependTo(list);
                            }
                            previous = e;
                            e.fadeIn(opts.animationDelay);
                        });

                        if (separator) {
                            separator.remove();
                        }

                        list.height('auto');

                        callback();
                    }
                }
            }

            var create = {
                entryElement: function(entry) {
                    var e = $('<li/>').html(entry.html).data('id', entry.id).hide();

                    if (detailPane) {
                        e.click(function() {
                            if (e.is('.loading') || e.is('.active')) {
                                return;
                            }
                            e.addClass('loading');

                            detailPane.trigger('display', [entry.url, function() {
                                e.removeClass('loading');
                                e.addClass('active');
                                if (activeEntry) {
                                    activeEntry.element.removeClass('active');
                                }
                                activeEntry = entry;
                            }]);
                        });
                    }
                    return e;
                },
                moreButton: function() {
                    var button = $('<span/>', {
                        class: 'more_button button disabled',
                        text: 'moar'
                    });
                    button.click(function() {
                        if (button.is('.disabled') || button.is('.loading')) {
                            return;
                        }
                        button.addClass('loading');

                        if (scrollable) {
                            if (!separator) {
                                separator = create.separator();
                            }
                            separator.hide().appendTo(list);
                        }

                        var callback = function() {
                            button.removeClass('loading');
                            if (scrollable) {
                                var scrollTo = self.height() - scrollable.height() + 10;
                                scrollable.animate({scrollTop: scrollTo}, 700);
                                separator.show();
                            }
                        }
                        fetchEntries(lastFeedList, handlers.pre.more,
                                     handlers.post.append, callback);
                    });
                    return button;
                },
                separator: function() {
                    return $('<li/>', {class: 'separator'});
                }
            }

            function removeEntry(entry) {
                delete entryMap[entry.id];
                entry.element.remove();
            }

            function fetchEntries(feedList, preHandler, postHandler, callback) {
                callback = callback || doNothing;

                var request = preHandler({feeds: feedList});

                $.get(opts.urls.get_entries, request, function(response) {

                    postHandler(response.entries, callback);

                    lastFeedList = feedList;

                    if (response.more) {
                        moreButton.removeClass('disabled');
                    } else {
                        moreButton.addClass('disabled');
                    }

                }, 'json');
            }

            function init() {
                moreButton = create.moreButton().insertAfter(list);
            }

            self.bind('fetch_init', function(event, feedList, callback) {
                fetchEntries(feedList, handlers.pre.nothing,
                             handlers.post.append, callback);
            });

            self.bind('fetch_select', function(event, feedList, callback) {
                fetchEntries(feedList, handlers.pre.sendLimit,
                             handlers.post.merge, callback);
            });

            self.bind('fetch_unselect', function(event, feedList, callback) {
                fetchEntries(feedList, handlers.pre.unselect,
                             handlers.post.merge, callback);
            });

            init();
        });
    }
    $.fn.entryList.defaults = {
        animationDelay: 100,
        getScrollableParent: function(self) {return self.parent().parent();}
    }
})(jQuery);
