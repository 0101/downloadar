;(function($){
    $.fn.downloadButton = function(options) {
        var opts = $.extend({}, $.fn.downloadButton.defaults, options);

        return this.each(function() {
            var self = $(this);
            var id = opts.getId.call(self);

            function download() {

                if (self.is('.loading')) { return }
                self.addClass('loading');

                opts.status.trigger('startLoadingAnimation');
                opts.status.trigger('info', 'Downloading .torrent...');

                $.post(opts.url, {'entry_id': id}, function(response) {
                    opts.status.trigger(response.status, [response.message]);
                    opts.getDisplay.call(self).html(response.html);
                    self.removeClass('loading');
                    opts.status.trigger('stopLoadingAnimation');
                    opts.list.trigger('update', [id]);
                }, 'json');

            }

            self.click(download);
        });
    }
    $.fn.downloadButton.defaults = {
        url: null,
        status: $(),
        list: $(),
        getId: function() { return this.attr('data-id'); },
        getDisplay: function() { return this.closest('.download_section'); }
    }
})(jQuery);
