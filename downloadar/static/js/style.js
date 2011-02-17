(function() {

    var viewport = $(window);
    var header = $('#main_header');

    $('#main_content .content_wrap').autoResize({
        getHeight: function() {
            return viewport.height() - header.height();
        }}
    );

    var entries = $('.half_wrap.entries');
    var detail = $('.half_wrap.detail');

    var entriesDefaultWidth = '40%';
    var detailDefaultWidth = '60%';

    function hideList() {
        entries.css('width', '0%');
        detail.css('width', '100%');
    }

    function showList() {
        entries.css('width', entriesDefaultWidth);
        detail.css('width', detailDefaultWidth);
    }

    $('#filter')
        .bind('empty', function() {
          //  if (detail.is('.empty'))
                hideList();

        })
        .bind('not_empty', function() {
                showList();
        });

})();
