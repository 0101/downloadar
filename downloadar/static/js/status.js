;(function($){
    $.fn.statusBar = function(options) {
        var opts = $.extend({}, $.fn.statusBar.defaults, options);

        return this.each(function() {
            var self = $(this);
            var content = self.find('.content');
            var statusHolder = self.find('.status_holder');

            function display(message, status) {
                content.text(message);
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

            self.bind('clear', function(event) {
                self.removeClass('loading');
                display('', '');
            });

            self.bind('start_loading_animation', function() {
                self.addClass('loading');
            });

            self.bind('stop_loading_animation', function() {
                self.removeClass('loading');
            });

            /* AJAX error handling */
            function onAjaxError(event, xhr, settings) {
                var debugReport = $(xhr.responseText);
                var message = xhr.status + ' ' + xhr.statusText;/* + ' ' +
                    debugReport.find('h1').text() + ': ' +
                    debugReport.find('pre.exception_value').text();*/

                if (xhr.status == 403) { message += ': ' + xhr.responseText; }

                display(message, 'error');
                // stop all loading animations
                $('.loading').removeClass('loading');
            }
            self.ajaxError(onAjaxError);

        });
    }
    $.fn.statusBar.defaults = {}
})(jQuery);
