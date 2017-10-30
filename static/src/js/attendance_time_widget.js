odoo.define("inspection.attendance_time", function (require) {

    var core = require("web.core");
    var Widget = require("web.Widget");

    var AttendanceTime = Widget.extend({
        start: function () {
            var height;
            if ($(".o_sub_menu")[0]) {
                height = ($(".o_sub_menu")[0].clientHeight) - 5;
            } else {
                var bodyHeight = $(document.body).height();
                var navbarHeight = $(".o_main_navbar")[0].clientHeight;
                height = bodyHeight - navbarHeight;
            }
            this.$el.append('<iframe src="/loading/google_map?flag=attendance_time" width="100%" height="' + height + 'px"></iframe>');
        }

    });

    core.action_registry.add("attendance_time", AttendanceTime);

});
