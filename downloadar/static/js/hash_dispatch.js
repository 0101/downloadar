$.hashDispatch = function(opts) {
    var lastSelected = null;

    opts.list.bind('entry_selected', function(e, entry) {
        window.location.hash = lastSelected = entry.id;
    })

    function getUrl(id) {
        return opts.entryUrl.replace('0', id);
    }

    function checkForChange() {
        var hash = window.location.hash;
        var match = window.location.hash.match(/^#([0-9]+)$/);
        if (match) {
            var id = match[1];
            if (id != lastSelected) {
                opts.list.trigger('select', [id, function(selected) {
                    if (!selected) {
                        opts.detailPane.trigger('display', [getUrl(id)]);
                        lastSelected = id;
                    } 
                }]);
            }
        }
    }

    checkForChange();

    window.setInterval(checkForChange, 400);

}
