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

                            detailPane.trigger('display', [entry.detail_url, function() {
                                e.removeClass('loading');
                                e.addClass('active');
                                if (activeEntry) {
                                    activeEntry.element.removeClass('active');
                                }
                                activeEntry = entry;
                            }]);

                            self.trigger('entry_selected', [entry]);
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
                                separator.show();
                                scrollable.scrollTo(separator, {duration: 635});
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

            function updateEntry(entry) {
                $.get(entry.url, {}, function(response) {
                    var oldEntry = entry;
                    var newEntry = response.entry;

                    newEntry.element = create.entryElement(newEntry);
                    entryMap[newEntry.id] = newEntry;
                    entries.splice(entries.indexOf(oldEntry), 1, newEntry);

                    newEntry.element
                        .insertBefore(oldEntry.element)
                        .attr('class', oldEntry.element.attr('class'))
                        .show();
                    oldEntry.element.remove();

                    if (oldEntry == activeEntry) {
                        activeEntry = newEntry;
                    }
                }, 'json');
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

            function bindKeyboard() {
                var LEFT = 37, UP = 38, RIGHT = 39, DOWN = 40;

                $(window).keydown(function(e) {
                    // TODO: scroll if entry out of viewport
                    var key = e.keyCode;
                    if (key == RIGHT || key == DOWN) {
                        self.trigger('next');
                        return false;
                    }
                    if (key == LEFT || key == UP) {
                        self.trigger('prev');
                        return false;
                    }
                });
            }

            function init() {
                moreButton = create.moreButton().insertAfter(list);
                bindKeyboard();
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

            self.bind('next', function(event) {
                if (!activeEntry) {
                    if (entries.length) {
                        entries[0].element.click();
                    }
                } else {
                    var index = entries.indexOf(activeEntry) + 1;
                    if (entries.length > index) {
                        entries[index].element.click();
                    } else {
                        moreButton.click();
                    }
                }
            });

            self.bind('prev', function(event) {
                if (!activeEntry) {
                    if (entries.length) {
                        entries[entries.length - 1].element.click();
                    }
                } else {
                    var index = entries.indexOf(activeEntry) - 1;
                    if (index >= 0) {
                        entries[index].element.click();
                    }
                }
            });

            self.bind('select', function(event, id, callback) {
                callback = callback || function() {};
                if (id in entryMap) {
                    entryMap[id].element.click();
                    callback(true);
                } else {
                    callback(false);
                }
            });

            self.bind('update', function(event, id) {
                if (id in entryMap) {
                    updateEntry(entryMap[id]);
                }
            });

            init();
        });
    }
    $.fn.entryList.defaults = {
        animationDelay: 100,
        getScrollableParent: function(self) {return self.parent().parent();}
    }
})(jQuery);
