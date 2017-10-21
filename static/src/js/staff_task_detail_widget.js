odoo.define("inspection.staff_task_detail", function (require) {

    var core = require("web.core");
    var Widget = require("web.Widget");

    var StaffTaskDetail = Widget.extend({
        start: function () {
            var height;
            if ($(".o_sub_menu")[0]) {
                height = ($(".o_sub_menu")[0].clientHeight) - 5;
            } else {
                var bodyHeight = $(document.body).height();
                var navbarHeight = $(".o_main_navbar")[0].clientHeight;
                height = bodyHeight - navbarHeight;
            }
            this.$el.append('<iframe src="/loading/google_map?flag=staff_task_detail" width="100%" height="' + height + 'px"></iframe>');
        }
    });

    core.action_registry.add("staff_task_detail", StaffTaskDetail);

});