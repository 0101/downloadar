;(function($){
    $.fn.statusBar = function(options) {
        var opts = $.extend({}, $.fn.statusBar.defaults, options);

        return this.each(function() {
            var self = $(this);
            var content = self.find('.content');
            var statusHolder = self.find('.status_holder');

            function display(message, status) {
                content.text(message)
                statusHolder.attr('class', 'status_holder ' + status);
            }

            self.bind('info', function(event, message) {
                display(message, 'info');
            });

            self.bind('error', function(event, message) {
                display(message, 'error');
            });

            self.bind('ok', function(event, message) {
                display(message, 'ok');
            });

            self.bind('startLoadingAnimation', function() {
                self.addClass('loading');
            });

            self.bind('stopLoadingAnimation', function() {
                self.removeClass('loading');
            });

        });
    }
    $.fn.statusBar.defaults = {}
})(jQuery);
