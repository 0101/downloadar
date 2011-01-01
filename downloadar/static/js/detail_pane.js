;(function($){
    $.fn.detailPane = function(options) {
        var opts = $.extend({}, $.fn.detailPane.defaults, options);

        var cache = {};

        return this.each(function() {
            var self = $(this);

            function display(html) {
                self.html(html);
            }

            self.bind('display', function(event, url, callback) {
                if (url in cache) {
                    display(cache[url]);
                    callback();
                } else {
                    $.get(url, {}, function(html) {
                        cache[url] = html;
                        display(html);
                        callback();
                    }, 'html');
                }
            });
        });
    }
    $.fn.detailPane.defaults = {}
})(jQuery);
