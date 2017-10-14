odoo.define("inspection.google_map", function (require) {
    "use strict";

    var core = require('web.core');
    var Widget = require('web.Widget');

    var GoogleMap = Widget.extend({

        start: function () {
            var height;
            if ($(".o_sub_menu")[0]) {
                height = ($(".o_sub_menu")[0].clientHeight) - 5;
            } else {
                var bodyHeight = $(document.body).height();
                var navbarHeight = $(".o_main_navbar")[0].clientHeight;
                height = bodyHeight - navbarHeight;
            }
            this.$el.append('<iframe src="/loading/google_map?flag=loading_google_map" width="100%" height="' + height + 'px"></iframe>');

        }
    });

    core.action_registry.add("google_map", GoogleMap);

});
