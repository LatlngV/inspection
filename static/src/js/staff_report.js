(function () {

    /* 存储巡线区名字的数组 */
    var departmentArray = [];
    /* 存储巡线区 id 的数组 */
    var departmentIdArray = [];
    /* 当前巡线区 */
    var currentDepartment;
    /* 当期报表是日报表还是其他报表 */
    var reportType = 1; // 1 是日报表  2 是月报表  3 是年报表，默认是日报表
    /* 当前视图类型 */
    var viewType = 1; // 1 是列表  2 是柱状图，默认是列表
    /* 获取当前日期 */
    $("#select_date").val(getDate());
    /* 获取巡线区 */
    getDepartment();
    /* 默认视图的点击事件 */
    onClick();
    /* 被选中员工的 id */
    var selectStaffId = 0;
    /* 范围的标志位 */
    var rangeFlag = 0;

    /**
     * 默认视图的点击事件
     */
    function onClick() {
        // 日报表的点击事件
        $("#day_report").click(function () {
            reportType = 1;
            $("#select_date").css("display", "inline-block").val(getDate());
            $("#select_month").css("display", "none");
            $("#select_year").css("display", "none");
            $(this).removeClass("btn-info");
            $("#month_report").addClass("btn-info");
            $("#year_report").addClass("btn-info");
            /* 获取数据 */
            getStaffReport();
        });
        // 月报表的点击事件
        $("#month_report").click(function () {
            reportType = 2;
            $("#select_date").css("display", "none");
            $("#select_month").css("display", "inline-block").val(getDate());
            $("#select_year").css("display", "none");
            $(this).removeClass("btn-info");
            $("#day_report").addClass("btn-info");
            $("#year_report").addClass("btn-info");
            /* 获取数据 */
            getStaffReport();
        });
        // 年报表的点击事件
        $("#year_report").click(function () {
            reportType = 3;
            $("#select_date").css("display", "none");
            $("#select_month").css("display", "none");
            $("#select_year").css("display", "inline-block").val(getDate());
            $(this).removeClass("btn-info");
            $("#day_report").addClass("btn-info");
            $("#month_report").addClass("btn-info");
            /* 获取数据 */
            getStaffReport();
        });
        // 列表的点击事件
        $("#list_view").click(function () {
            viewType = 1;
            $(this).removeClass("btn-warning");
            $("#bar_view").addClass("btn-warning");
            /* 获取数据 */
            getStaffReport();
        });
        // 柱状图的点击事件
        $("#bar_view").click(function () {
            viewType = 2;
            $(this).removeClass("btn-warning");
            $("#list_view").addClass("btn-warning");
            /* 获取数据 */
            getStaffReport();
        });
        $("#taskDetailModal").on("hidden.bs.modal", function () {
            $("#taskDetailTbody").html("");
            var tr = document.getElementById("taskDetailThead");
            var nodeList = document.getElementsByClassName("dotopTh");
            for (i = nodeList.length - 1; i >= 0; i--) {
                tr.removeChild(nodeList[i]);
            }
        });
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
                    var container = document.getElementById("tab_layout");
                    for (var i = 0; i < json.length; i++) {
                        var data = json[i];
                        var li = document.createElement("li");
                        var a = document.createElement("a");
                        a.href = "#";
                        a.innerHTML = data.departmentName;
                        li.appendChild(a);
                        var departmentId = data.departmentId;
                        if (i === 0) {
                            currentDepartment = departmentId;
                            li.className = "active";
                        }
                        container.appendChild(li);
                        departmentArray.push(data.departmentName);
                        departmentIdArray.push(departmentId);
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
        var liArray = document.getElementsByTagName("a");
        for (var i = 0; i < liArray.length; i++) {
            liArray[i].onclick = function () {
                // 先把所有带有 active class 的移除
                for (var k = 0; k < liArray.length; k++) {
                    liArray[k].parentNode.classList.remove("active");
                }
                for (var j = 0; j < departmentArray.length; j++) {
                    if (this.innerHTML === departmentArray[j]) {
                        this.parentNode.classList.add("active");
                        currentDepartment = departmentIdArray[j];
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
                console.log(json);
                if (json !== null && json.length > 0) {
                    var staffArray = [];
                    var departmentArray = [];
                    var pipelineArray = [];
                    var totalKiloArray = [];
                    var staffPointArray = [];
                    var totalPointArray = [];
                    var defaultArray = [];
                    var defaultPercArray = [];
                    var oneHundredArray = [];
                    var onePercArray = [];
                    var twoHundredArray = [];
                    var twoPercArray = [];
                    var fiveHundredArray = [];
                    var fivePercArray = [];
                    var thousandArray = [];
                    var thousandPercArray = [];
                    var staffIdArray = [];
                    for (var i = 0; i < json.length; i++) {
                        var data = json[i];
                        var staffName = data.staffName;
                        var totalPoint = data.totalPoint;
                        var defaultCount = data.defaultCount;
                        var oneHundredCount = data.oneHundredCount;
                        var twoHundredCount = data.twoHundredCount;
                        var fiveHundredCount = data.fiveHundredCount;
                        var thousandCount = data.thousandCount;
                        var defaultPerc = defaultCount / totalPoint;
                        var onePerc = oneHundredCount / totalPoint;
                        var twoPerc = twoHundredCount / totalPoint;
                        var fivePerc = fiveHundredCount / totalPoint;
                        var thousandPerc = thousandCount / totalPoint;
                        var staffId = data.staffId;
                        if (totalPoint === 0) {
                            defaultPerc = 0;
                            onePerc = 0;
                            twoPerc = 0;
                            fivePerc = 0;
                            thousandPerc = 0;
                        }
                        staffArray.push(staffName);
                        departmentArray.push(data.deparment);
                        pipelineArray.push(data.pipelineLength);
                        totalKiloArray.push(data.totalKilo);
                        staffPointArray.push(data.pointCount);
                        totalPointArray.push(totalPoint);
                        defaultArray.push(defaultCount);
                        defaultPercArray.push(defaultPerc.toFixed(2) + "%");
                        oneHundredArray.push(oneHundredCount);
                        onePercArray.push(onePerc.toFixed(2) + "%");
                        twoHundredArray.push(twoHundredCount);
                        twoPercArray.push(twoPerc.toFixed(2) + "%");
                        fiveHundredArray.push(fiveHundredCount);
                        fivePercArray.push(fivePerc.toFixed(2) + "%");
                        thousandArray.push(thousandCount);
                        thousandPercArray.push(thousandPerc.toFixed(2) + "%");
                        staffIdArray.push(staffId);
                    }
                    var listView = document.getElementById("report_list");
                    var barView = document.getElementById("report_bar");
                    if (viewType === 1) { // 列表
                        // 隐藏柱状图，显示列表视图
                        listView.style.display = "";
                        barView.style.display = "none";
                        // 在列表视图上显示数据
                        showListView(staffArray, departmentArray, pipelineArray, totalKiloArray, staffPointArray, totalPointArray, defaultArray, defaultPercArray, oneHundredArray, onePercArray, twoHundredArray, twoPercArray, fiveHundredArray, fivePercArray, thousandArray, thousandPercArray, staffIdArray);
                    } else if (viewType === 2) { // 柱状图
                        // 隐藏列表视图，显示柱状
                        listView.style.display = "none";
                        barView.style.display = "";
                        // 在柱状图上显示数据
                        showBarView(barView, staffArray, totalPointArray, defaultArray, oneHundredArray, twoHundredArray, fiveHundredArray, thousandArray);
                    }
                } else {
                    var tbody = document.getElementById("staff_data");
                    tbody.innerHTML = "";
                }
            }
        });
    }

    /**
     * 列表视图
     */
    function showListView(staffArray, departmentArray, pipelineArray, totalKiloArray, staffPointArray, totalPointArray, defaultArray, defaultPercArray, oneHundredArray, onePercArray, twoHundredArray, twoPercArray, fiveHundredArray, fivePercArray, thousandArray, thousandPercArray, staffIdArray) {
        var tbody = document.getElementById("staff_data");
        tbody.innerHTML = "";
        for (var i = 0; i < staffArray.length; i++) {
            var tr = document.createElement("tr");
            tr.height = 40;
            for (var j = 0; j < 16; j++) {
                var td = document.createElement("td");
                td.style.paddingLeft = "5px";
                var a = document.createElement("a");
                a.dataset.toggle = "modal";
                a.dataset.target = "#reportModal";
                a.style.cursor = "pointer";
                a.innerHTML = defaultArray[i];
                a.href = staffIdArray[i];
                if (j === 0) {
                    td.innerHTML = staffArray[i];
                }
                if (j === 1) {
                    td.innerHTML = departmentArray[i];
                }
                if (j === 2) {
                    td.innerHTML = pipelineArray[i];
                }
                if (j === 3) {
                    td.innerHTML = totalKiloArray[i];
                }
                if (j === 4) {
                    td.innerHTML = staffPointArray[i];
                }
                if (j === 5) {
                    td.innerHTML = totalPointArray[i];
                }
                if (j === 6) {
                    if (reportType === 1) {
                        a.onclick = function () {
                            aClick(this.href, 1);
                        };
                        td.appendChild(a);
                    } else {
                        td.innerHTML = defaultArray[i];
                    }
                }
                if (j === 7) {
                    td.innerHTML = defaultPercArray[i];
                }
                if (j === 8) {
                    if (reportType === 1) {
                        a.onclick = function () {
                            aClick(this.href, 2);
                        };
                        td.appendChild(a);
                    } else {
                        td.innerHTML = defaultArray[i];
                    }
                }
                if (j === 9) {
                    td.innerHTML = onePercArray[i];
                }
                if (j === 10) {
                    if (reportType === 1) {
                        a.onclick = function () {
                            aClick(this.href, 3);
                        };
                        td.appendChild(a);
                    } else {
                        td.innerHTML = defaultArray[i];
                    }
                }
                if (j === 11) {
                    td.innerHTML = twoPercArray[i];
                }
                if (j === 12) {
                    if (reportType === 1) {
                        a.onclick = function () {
                            aClick(this.href, 4);
                        };
                        td.appendChild(a);
                    } else {
                        td.innerHTML = defaultArray[i];
                    }
                }
                if (j === 13) {
                    td.innerHTML = fivePercArray[i];
                }
                if (j === 14) {
                    if (reportType === 1) {
                        a.onclick = function () {
                            aClick(this.href, 5);
                        };
                        td.appendChild(a);
                    } else {
                        td.innerHTML = defaultArray[i];
                    }
                }
                if (j === 15) {
                    td.innerHTML = thousandPercArray[i];
                }
                tr.appendChild(td);
            }
            tbody.appendChild(tr);
        }
    }

    /**
     * a 标签的点击事件
     *
     * @param content 内容
     * @param flag 标志位
     */
    function aClick(content, flag) {
        var textArray = content.split("/");
        for (var i = 0; i < textArray.length; i++) {
            if (i === textArray.length - 1) {
                rangeFlag = flag;
                selectStaffId = textArray[i];
                // 显示巡线员数据
                showStaffPointData();
            }
        }
    }

    /**
     * 显示巡线员必经点完成情况
     */
    function showStaffPointData() {
        // 往 table 中的 thead 中添加相应数据
        $.ajax({
            url: "/show_button",
            data: {},
            dataType: "json",

            success: function (json) {
                if (json !== null && json.length > 0) {
                    var theadTr = document.getElementById("taskDetailThead");
                    for (var i = 0; i < json.length; i++) {
                        var data = json[i];
                        var attendance_name = data.attendance_name;
                        var th = document.createElement("th");
                        th.className = "dotopTh";
                        th.innerHTML = attendance_name;
                        theadTr.appendChild(th);
                    }
                }
                // 往 table 中的 tbody 中添加相应数据
                showTbodyData();
            }
        });
    }

    /**
     * 把数据插入到 tbody 中
     */
    function showTbodyData() {
        $.ajax({
            url: "/task_detail",
            data: {staffId: selectStaffId, "date": $("#select_date").val(), "rangeFlag": rangeFlag},
            dataType: "json",

            success: function (json) {
                if (json !== null && json.length > 0) {
                    var tbody = document.getElementById("taskDetailTbody");
                    for (var i = 0; i < json.length; i++) {
                        var data = json[i];
                        var tr = document.createElement("tr");
                        for (j = 0; j < 4; j++) {
                            var td = document.createElement("td");
                            var span = document.createElement("span");
                            if (data.morning === "0") {
                                span.style.color = "#00FF00";
                            } else if (data.morning === "1") {
                                span.style.color = "#FF0000";
                            }
                            if (j === 0) {
                                td.innerHTML = data.pointName;
                            }
                            if (j === 1) {
                                td.innerHTML = data.latlng;
                            }
                            if (j === 2) {
                                span.innerHTML = data.morning;
                                td.appendChild(span)
                            }
                            if (j === 3) {
                                span.innerHTML = data.afternoon;
                                td.appendChild(span)
                            }
                            tr.appendChild(td);
                        }
                        tbody.appendChild(tr);
                    }
                }
                $("#taskDetailModal").modal("show");
            }
        });
    }

    /**
     * 柱状图
     *
     * @param barView div 对象
     * @param staffArray 巡线员数组
     * @param totalPointArray 总共巡线点
     * @param defaultArray 默认范围内
     * @param oneHundredArray 一百米范围内
     * @param twoHundredArray 两百米范围内
     * @param fiveHundredArray 五百米范围内
     * @param thousandArray 一千米范围内
     */
    function showBarView(barView, staffArray, totalPointArray, defaultArray, oneHundredArray, twoHundredArray, fiveHundredArray, thousandArray) {
        // 初始化 echarts 实例
        var barChart = echarts.init(barView);

        // 指定图表的配置项和数据
        var option = {
            // 左上角标题
            title: {
                text: "巡线员柱状图报表"
            },
            // 显示柱状图的颜色
            color: ["#FF0000", "#00FF00", "#0000FF", "#00FFFF", "#FF00FF", "#FFFF00"],
            // 鼠标放到相应的位置显示相应的数据
            tooltip: {
                trigger: "axis",
                axisPointer: {
                    type: "shadow"
                }
            },
            // 上方的提示，与柱状图相关
            legend: {
                data: ["必经点总数", "默认范围", "100米", "200米", "500米", "1000米"]
            },
            calculable: true,
            // x 轴显示的数据
            xAxis: [
                {
                    data: staffArray
                }
            ],
            yAxis: [
                {}
            ],
            // 在坐标系内显示的数据
            series: [
                {
                    name: "必经点总数",    // 与 legend 相关
                    type: 'bar',          // 显示为柱状图
                    barGap: 0,            // 每个圆柱之间的间距
                    data: totalPointArray // 相应的数据
                },
                {
                    name: "默认范围",
                    type: 'bar',
                    barGap: 0,
                    data: defaultArray
                },
                {
                    name: "100米",
                    type: 'bar',
                    barGap: 0,
                    data: oneHundredArray
                },
                {
                    name: "200米",
                    type: 'bar',
                    barGap: 0,
                    data: twoHundredArray
                },
                {
                    name: "500米",
                    type: 'bar',
                    barGap: 0,
                    data: fiveHundredArray
                },
                {
                    name: "1000米",
                    type: 'bar',
                    barGap: 0,
                    data: thousandArray
                }
            ]
        };
        // 使用刚指定的配置项和数据显示图表
        if (option && typeof option === "object") {
            barChart.setOption(option, true);
        }
    }

    /**
     * 年月日
     */
    function getDate() {
        var date = new Date();
        var year = date.getFullYear();
        var month = date.getMonth() + 1;
        var day = date.getDate() - 1;
        if (reportType === 1) { // 年月日
            return year + "-" + month + "-" + day;
        } else if (reportType === 2) { // 年月
            return year + "-" + month;
        } else if (reportType === 3) { // 年
            return year;
        }
    }

}());