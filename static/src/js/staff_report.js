(function () {

    /* 存储巡线区名字的数组 */
    var departmentArray = [];
    /* 存储巡线区 id 的数组 */
    var departmentId = [];
    /* 当前巡线区 */
    var currentDepartment = 1;
    /* 当期报表是日报表还是其他报表 */
    var reportType = 1; // 1 是日报表  2 是月报表  3 是年报表，默认是日报表
    /* 当前视图类型 */
    var viewType = 1; // 1 是列表  2 是柱状图，默认是列表
    /* 获取巡线区 */
    getDepartment();
    /* 默认视图的点击事件 */
    onClick();

    /**
     * 默认视图的点击事件
     */
    function onClick() {
        // 日报表的点击事件
        $(".day_report").click(function () {
            reportType = 1;
        });
        // 月报表的点击事件
        $(".month_report").click(function () {
            reportType = 2;
        });
        // 年报表的点击事件
        $(".year_report").click(function () {
            reportType = 3;
        });
        // 列表的点击事件
        $(".list_view").click(function () {
            viewType = 1;
        });
        // 柱状图的点击事件
        $(".bar_view").click(function () {
            viewType = 2;
        });

        /* 获取数据 */
        getStaffReport();
    }

    /**
     * 获取巡线区
     */
    function getDepartment() {
        $.ajax({
            url: "/staff_department",
            data: {},
            dataType: "json",

            success: function (json) {
                if (json !== null && json.length > 0) {
                    var container = document.getElementById("ul");
                    for (var i = 0; i < json.length; i++) {
                        var data = json[i];
                        var li = document.createElement("li");
                        li.className = "dotop_li";
                        li.innerHTML = data.departmentName;
                        container.appendChild(li);
                        departmentArray.push(data.departmentName);
                        departmentId.push(data.dapartmentId);
                        if (i === 0) {
                            currentDepartment = data.departmentId;
                        }

                    }
                    /* 巡线区的点击事件 */
                    departmentOnclick();
                    /* 默认显示第一个巡线区的数据 */
                    getStaffReport();
                }
            }
        });
    }

    /**
     * 巡线区的点击事件
     */
    function departmentOnclick() {
        var liArray = document.getElementsByClassName("dotop_li");
        for (var i = 0; i < li.length; i++) {
            liArray[i].onclick = function () {
                for (var j = 0; j < departmentArray.length; j++) {
                    if (this.innerHTML === departmentArray[j]) {
                        currentDepartment = departmentId[j];
                        /* 获取相应数据 */
                        getStaffReport();
                    }
                }
            }
        }
    }

    /**
     * 巡线员的报表数据
     */
    function getStaffReport() {
        $.ajax({
            url: "/staff_report",
            data: {departmentId: currentDepartment, reportType: reportType, date: getDate()},
            dataType: "json",

            success: function (json) {
                if (json !== null && json.length > 0) {
                    for (var i = 0; i < json.length; i++) {
                        var data = json[i];
                        // TODO 添加巡线员数据

                    }
                    if (viewType === 1) { // 列表
                        // 显示列表视图，隐藏柱状图
                        // 在列表视图上显示数据
                    } else if (viewType === 2) { // 柱状图
                        // 显示柱状图，隐藏列表视图
                        // 在柱状图上显示数据
                    }
                }
            }
        });
    }

    /**
     * 年月日
     */
    function getDate() {
        var date = new Date();
        var year = date.year;
        var month = date.month;
        var day = date.day;
        if (reportType === 1) { // 年月日
            return "";
        } else if (reportType === 2) { // 年月
            return "";
        } else if (viewType === 3) { // 年
            return "";
        }
    }

}());