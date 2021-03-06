;(function($){
    $.fn.downloadButton = function(options) {
        var opts = $.extend({}, $.fn.downloadButton.defaults, options);

        return this.each(function() {
            var self = $(this);

            function download() {
                if (self.is('.loading')) { return }
                self.addClass('loading');

                opts.status.trigger('start_loading_animation');
                opts.status.trigger('info', 'downloading .torrent');

                $.post(opts.url, {'entry_id': opts.id}, function(response) {
                    opts.status.trigger(response.status, [response.message]);
                    opts.getDisplay.call(self).html(response.html);
                    opts.detailPane.trigger('clear_cache');
                    self.removeClass('loading');
                    opts.status.trigger('stop_loading_animation');
                    opts.list.trigger('update', [opts.id]);
                }, 'json');
            }

            self.click(download);
        });
    }
    $.fn.downloadButton.defaults = {
        id: null,
        url: null,
        entryDetailUrl: null,
        status: $(),
        list: $(),
        getDisplay: function() { return this.closest('.download_section_containter'); }
    }
})(jQuery);
