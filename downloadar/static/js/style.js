jQuery(function($){
    var contentWrap = $('#main_content .content_wrap');
    var header = $('#main_header');
    var viewport = $(window);

    function adjustContentWrapHeight(){

        var height = viewport.height() - header.height();

        contentWrap.height(height);
    }

    viewport.resize(adjustContentWrapHeight);

    adjustContentWrapHeight();
});
