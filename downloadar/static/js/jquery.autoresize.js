;(function($){
    $.fn.autoResize = function(options) {
        var opts = $.extend({}, $.fn.autoResize.defaults, options);
        var viewport = $(window);

        return this.each(function() {
            var self = $(this);

            function resize(){
                if (opts.getHeight) {
                    var height = opts.getHeight.call(this);
                    self.height(height);
                }
                if (opts.getWidth) {
                    var width = opts.getWidth.call(this);
                    self.width(width);
                }
            }
            $(document).ready(resize);
            viewport.resize(resize);
        });
    }
    $.fn.autoResize.defaults = {
        getHeight: null,
        getWidth: null
    }
})(jQuery);
