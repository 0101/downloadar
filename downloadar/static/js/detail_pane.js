;(function($){
    $.fn.detailPane = function(options) {
        var opts = $.extend({}, $.fn.detailPane.defaults, options);

        var cache = {};

        return this.each(function() {
            var self = $(this);
            var contentWrap = self.closest('.content_wrap');

            function display(html) {
                self.html(html);
            }

            self.bind('display', function(event, url, callback) {
                callback = callback || function() {};
                if (url in cache) {
                    display(cache[url]);
                    callback();
                } else {
                    var loadingTimeout = window.setTimeout(function() {
                        contentWrap.addClass('loading');
                    }, 150);
                    $.get(url, {}, function(html) {
                        cache[url] = html;
                        display(html);
                        callback();
                        window.clearTimeout(loadingTimeout);
                        contentWrap.removeClass('loading');
                    }, 'html');
                }
            });

            self.bind('clear_cache' , function(event, url) {
                console.log(cache, url);
                delete cache[url];
            });

        });
    }
    $.fn.detailPane.defaults = {}
})(jQuery);
