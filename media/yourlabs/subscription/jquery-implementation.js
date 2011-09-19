Subscription = function(url, override) {
    instance = $.extend({
        'delay': 3000,
        'url': url,
        'refresh': function() {
            var url = Subscription.singleton.url + '?x=' + Math.round(new Date().getTime());
            $.getJSON(url, function(data, text_status, jq_xhr) {
                $(document).trigger('subscription.refresh', [data, text_status, jq_xhr]);
            });
        },
        'bind_refresh': function() {
            $(document).bind('subscription.refresh', Subscription.singleton.process_all);
            $(document).bind('subscription.refresh', Subscription.singleton.set_timeout);
        },
        'set_timeout': function() {
            setTimeout(function() {
                Subscription.singleton.refresh()
            }, Subscription.singleton.delay);
        },
        'process_all': function(e, data, text_status, jq_xhr) {
            for(var key in data) {
                $(document).trigger('subscription.process', [data, key]);
            }
        },

        'bind_process': function() {
            $(document).bind('subscription.process', Subscription.singleton.set_count);
        },
        'set_count': function(e, data, key) {
            if (! key.match(/_count$/)) {
                return;
            }

            var el = Subscription.singleton.get_count_selector(data, key);
            if (el.length && data[key] > 0) {
                el.html(data[key]);
                el.addClass('hilight');
            }
        },
        'get_count_selector': function(data, i) {
            return $('.subscription_notifications .' + i.replace('_count', '') + ' .count');
        },
        'notifications': [],
    }, override);

    return instance
}

Subscription.factory = function(url, override) {
    Subscription.singleton = Subscription(url, override);
    Subscription.singleton.bind_refresh();
    Subscription.singleton.bind_process();
    Subscription.singleton.refresh();
}
