(function() {

    var viewport = $(window);
    var header = $('#main_header');

    $('#main_content .content_wrap').autoResize({
        getHeight: function() {
            return viewport.height() - header.height();
        }}
    );

})();
