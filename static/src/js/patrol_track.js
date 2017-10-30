/* 地图对象 */
var map = null;
/* 开始轨迹回放的标志位 */
var startFlag = false;
/* 历史轨迹的点 */
var historyPoint = [];
/* 播放到那个点的角标 */
var index = 0;
/* 信息窗口 */
var infoWindow = new google.maps.InfoWindow({});
/* 谷歌地图中 marker 中要显示的文本内容 */
var markerContent = [];
/* 历史轨迹中显示巡线员的 Marker */
var historyMarker = new google.maps.Marker({});
/* 管道画的线 */
var historyPolyline = null;
/* 存储 marker 的数组 */
var markerPoint = [];
/* 存储管道的数组 */
var allPolyline = [];
/* 轨迹回放的开始时间 */
var startTime = "";
/* 轨迹回放的结束时间 */
var endTime = "";
/* 经度坐标 */
var mLongitude = 0;
/* 纬度坐标 */
var mLatitude = 0;
/* 巡线员名字 */
var mStaffName = null;
/* 最后一次的 GPS 时间 */
var mGpsTime = 0;
/* 更新巡线员巡线轨迹的 Marker 数组 */
var updateHistoryMarker = [];
/* 更新巡线员巡线轨迹的点 */
var updateHistoryPoint = [];
/* 更新巡线员巡线轨迹的线 */
var updateHistoryPolyline = null;

/**
 * 初始化谷歌地图
 */
function initGoogleMap() {
    map = new google.maps.Map(document.getElementById("odoo-google-map"), {
        zoom: 9,
        center: {lat: 36.9222760000, lng: 119.1296490000},
        mapTypeId: google.maps.MapTypeId.HYBRID
    });

    historyMarker.setMap(map);
    historyMarker.setIcon("/inspection/static/src/img/blue_01.png");

    $("#date_start").val(getCurrentDate(true) + " " + "08:00:00");
    $("#date_end").val(getCurrentDate(false));

    // 根据考勤时间动态设置 button 个数
    setButtonNumber();
    // 根据坐标画管道
    drawPipeline();
    // 绘制巡线员必经点
    drawStaffPoint();
    // 显示右侧菜单栏数据
    showRightDrawerData();
    // 如果选择了员工，显示对应员工的线路和历史轨迹
    if (staffId !== 0) {
        selectRoute();
    }
}

/**
 * 根据考勤时间动态设置 button 个数
 */
function setButtonNumber() {
    var divContainer = document.getElementById("divContainer");
    $.ajax({
        url: "/show_button",
        data: {},
        dataType: "json",

        success: function (json) {
            if (json !== null && json.length > 0) {
                var attendance_time = [];
                for (var i = 0; i < json.length; i++) {
                    var data = json[i];
                    var attendance_name = data.attendance_name;
                    var button = document.createElement("button");
                    button.innerHTML = attendance_name;
                    button.className = "dotop_button";
                    button.style.verticalAlign = "middle";
                    button.style.background = "#E8E8E8";
                    if (i > 0) {
                        button.style.marginLeft = "5px";
                    }
                    divContainer.appendChild(button);
                    attendance_time.push({
                        "attendance_name": attendance_name,
                        "attendance_start_time": data.attendance_start_time,
                        "attendance_end_time": data.attendance_end_time
                    });
                }

                /*
                 * 这是 button 的点击事件，只有点击之后才会有效，
                 * 此时需要给轨迹回放的开始时间和结束时间一个默认值
                 */
                startTime = $("#date_start").val();
                endTime = $("#date_end").val();

                var buttonArray = document.getElementsByClassName("dotop_button");
                if (buttonArray !== null && buttonArray.length > 0) {
                    for (var i = 0; i < buttonArray.length; i++) {
                        buttonArray[i].onclick = function () {
                            for (var j = 0; j < attendance_time.length; j++) {
                                buttonArray[j].style.background = "#E8E8E8";
                                if (this.innerHTML === attendance_time[j].attendance_name) {
                                    if (staffId !== 0) {
                                        startTime = attendance_time[j].attendance_start_time;
                                        endTime = attendance_time[j].attendance_end_time;
                                        $("#date_start").val(startTime);
                                        $("#date_end").val(endTime);
                                        showRoute();
                                        this.style.background = "#97FFFF";
                                    } else {
                                        alert("请先选择人员!");
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    });
}

/**
 * 获取当前年月日
 */
function getCurrentDate(flag) {
    var date = new Date();
    var year = date.getFullYear();
    var month = appendNumber(date.getMonth() + 1);
    var day = appendNumber(date.getDate());
    var currentDate = year + "-" + month + "-" + day;
    if (flag) {
        return currentDate;
    } else {
        var hour = appendNumber(date.getHours());
        var minute = appendNumber(date.getMinutes());
        var second = appendNumber(date.getSeconds());
        return currentDate + " " + hour + ":" + minute + ":" + second
    }
}

/**
 * 拼接字符串
 */
function appendNumber(argument) {
    if (argument > 0 && argument < 10) {
        return "0" + argument;
    } else {
        return argument
    }
}

/**
 * 根据坐标画管道
 */
function drawPipeline() {
    $.ajax({
        url: "/staff_line",
        data: {},
        dataType: "json",

        success: function (json) {
            if (json !== null && json.length > 0) {
                var json_length = json.length;
                for (var i = 0; i < json_length; i++) {
                    var line_point = [];
                    var datas = json[i];
                    var latlng = datas.latlng;

                    for (var j = 0; j < latlng.length; j++) {
                        // 获取管道点
                        var data = latlng[j];
                        line_point.push(new google.maps.LatLng(data.latitude, data.longitude));
                    }
                    var lineId = datas.id;
                    // 画管线
                    var tmpPolyline = new google.maps.Polyline({
                        path: line_point,
                        strokeColor: "#0000FF",
                        strokeWeight: 5,
                        strokeOpacity: 1
                    });
                    tmpPolyline.setMap(map);
                    allPolyline.push({line_id: lineId, polyline: tmpPolyline})
                }
            }
        },
        error: function () {
            alert("没有获取到相应数据，请检查网络或者刷新重试!");
        }
    });
}

/**
 * 绘制巡线员必经点
 */
function drawStaffPoint() {
    $.ajax({
        url: "/staff_point",
        data: {},
        dataType: "json",

        success: function (json) {
            if (json !== null && json.length > 0) {
                var jsonLength = json.length;
                var latlng = [];
                for (var i = 0; i < jsonLength; i++) {
                    var data = json[i];
                    var latitude = data.latitude;
                    var longitude = data.longitude;
                    var latlngMarker = new google.maps.Marker({
                        position: new google.maps.LatLng(latitude, longitude),
                        map: map,
                        title: data.pointName,
                        icon: "/inspection/static/src/img/icon_03.png"
                    });
                    latlng.push({id: data.id, tmp_task_marker: latlngMarker});
                }
            }
        }
    });
}

/**
 * 右侧菜单栏展示数据
 */
function showRightDrawerData() {
    $.ajax({
        url: "/show_all_employees",
        data: {},
        dataType: "json",

        success: function (json) {
            $("#tree").treeview({
                data: json,

                onNodeSelected: function (event, node) {
                    staffId = node.staff_id;
                    index = 0;
                    mGpsTime = 0;
                    /* 根据巡线员 id 显示其对应的管道数据 */
                    selectRoute();
                },
                onNodeUnselected: function () {
                    staffId = 0;
                    mGpsTime = 0;
                }
            });
        }
    });
}

/**
 * 根据巡线员的 id 获取相应的管线数据
 */
function getLineNumber() {
    $.ajax({
        url: "/line_position",
        data: {staff_id: staffId},
        dataType: "json",

        success: function (json) {
            var lineId = json.line_id;
            for (var i = 0; i < allPolyline.length; i++) {
                if (allPolyline[i].line_id === lineId) {
                    var path = allPolyline[i].polyline.getPath();
                    allPolyline[i].polyline.setOptions({
                        path: path,
                        strokeColor: "#8B3626",
                        strokeWeight: 5,
                        strokeOpacity: 1
                    });
                }
            }
        }
    });
}

/**
 * 重置管道为蓝色
 */
function setAllPolyline() {
    if (allPolyline.length > 0) {
        for (var i = 0; i < allPolyline.length; i++) {
            var path = allPolyline[i].polyline.getPath();
            allPolyline[i].polyline.setOptions({
                path: path,
                strokeColor: "#0000FF",
                strokeWeight: 5,
                strokeOpacity: 1
            });
        }
    }
}

/**
 * 选择线路
 */
function selectRoute() {
    if (staffId === 0) {
        alert("请先选择人员!");
    } else {
        /* 显示历史轨迹线路 */
        showRoute();
    }
}

/**
 * 显示历史轨迹线路
 */
function showRoute() {
    /* 将管道重置为蓝色 */
    setAllPolyline();

    $.ajax({
        url: "/show_track",
        data: {
            staff_id: staffId,
            begin_time: $("#date_start").val(),
            end_time: $("#date_end").val()
        },
        type: "post",
        dataType: "json",

        success: function (json) {
            /* 获取对应管线 */
            getLineNumber();

            if (json !== null && json.length > 0) {
                // 清空数组
                historyPoint.splice(0, historyPoint.length);
                // 清空线
                if (historyPolyline !== null) {
                    historyPolyline.setMap(null);
                }
                // 清空 InfoWindow 里的信息
                if (markerContent.length > 0) {
                    markerContent.splice(0, markerContent.length);
                }
                // 清空 marker
                if (markerPoint.length > 0) {
                    for (var i = 0; i < markerPoint.length; i++) {
                        markerPoint[i].tmp_task_marker.setMap(null);
                    }
                    markerPoint.splice(0, markerPoint.length);
                }
                var jsonLength = json.length;
                for (var i = 0; i < jsonLength; i++) {
                    var data = json[i];
                    var latitude = data.latitude;
                    var longitude = data.longitude;
                    var speed = data.speed;
                    var icon = null;
                    if (speed === 0) {
                        icon = "/inspection/static/src/img/route_gray.png"
                    } else if (speed > 35) {
                        icon = "/inspection/static/src/img/route_red.png";
                    } else {
                        icon = "/inspection/static/src/img/route_green.png";
                    }

                    var historyPointMarker = new google.maps.Marker({
                        position: new google.maps.LatLng(latitude, longitude),
                        map: map,
                        icon: icon
                    });
                    // 文本内容
                    var gpsTime = data.gps_time;
                    if (i === jsonLength - 1) {
                        mGpsTime = gpsTime;
                    }

                    var dateTime = timeStamp2dateTime(gpsTime);
                    var content = "<div><span style='font-weight: bold;'>巡线人员: </span>" + data.staff + "</div>";
                    content += "<div><span style='font-weight: bold;'>纬度坐标: </span>" + latitude + "</div>";
                    content += "<div><span style='font-weight: bold;'>经度坐标: </span>" + longitude + "</div>";
                    content += "<div><span style='font-weight: bold;'>速度: </span>" + speed + " km/h</div>";
                    content += "<div><span style='font-weight: bold;'>时间: </span>" + dateTime + "</div>";
                    content += "<div style='margin-top: 3px;'><span><a href='#' onclick='setStaffPoint()'>设为必经点</a></span></div>";
                    markerContent.push(content);

                    markerPoint.push({tmp_task_marker: historyPointMarker});
                    historyPoint.push(new google.maps.LatLng(latitude, longitude));

                    showInfoWindow(historyPointMarker, content, latitude, longitude, data.staff);
                }
                // 画巡线轨迹
                historyPolyline = new google.maps.Polyline({
                    path: historyPoint,
                    strokeColor: "#FFA500",
                    strokeWeight: 5,
                    strokeOpacity: 1
                });
                historyPolyline.setMap(map);
                map.setCenter(historyPoint[index]);
                map.setZoom(18);

                /* 更新巡线员巡线轨迹 */
                updateHistory();
            } else {
                alert("此时间段暂无管道数据!");
            }
        }
    });
}

/**
 * 将时间戳转换为日期
 *
 * @param timeStamp 时间戳
 * @returns {string} 时间日期字符串
 */
function timeStamp2dateTime(timeStamp) {
    var date = new Date(parseInt(timeStamp) * 1000);
    var year = date.getFullYear();
    var month = date.getMonth() + 1;
    var day = date.getDate();
    var hour = date.getHours();
    var minute = date.getMinutes();
    var second = date.getSeconds();
    return year + "-" + month + "-" + day + " " + add(hour) + ":" + add(minute) + ":" + add(second);
}

function add(time) {
    if (time < 10) {
        return "0" + time;
    }
    return time
}

/**
 * 设置必经点
 */
function setStaffPoint() {
    $("#staffName").val(mStaffName);
    $("#latitude").val(mLatitude);
    $("#longitude").val(mLongitude);
    // 弹出模态框
    $("#staffPointlModal").modal();
}

/**
 * 保存必经点
 */
function saveStaffPoint() {
    // 获取相应必经点的数据
    $.ajax({
        url: "/save_staff_point",
        data: {
            staffId: staffId,
            latitude: $("#latitude").val(),
            longitude: $("#longitude").val(),
            pointName: $("#pointName").val(),
            attendanceRange: $("#attendanceRange").val()
        },
        type: "post",
        dataType: "json",

        success: function (json) {
            if (json !== null && json.length !== 0) {
                if (json.response === "success") {
                    $("#staffPointlModal").modal("hide");
                }
            }
        }
    });
}

/**
 * 打开信息窗口
 *
 * @param marker 覆盖物
 * @param content 显示的文本内容
 * @param latitude 纬度坐标
 * @param longitude 经度坐标
 * @param staffName 巡线员名字
 */
function showInfoWindow(marker, content, latitude, longitude, staffName) {
    google.maps.event.addListener(marker, "click", function () {
        map.setCenter(marker.getPosition());
        infoWindow.setContent(content);
        mLatitude = latitude;
        mLongitude = longitude;
        mStaffName = staffName;
        infoWindow.open(map, marker);
    });
}

/**
 * 开始回放
 */
function startPlay() {
    startFlag = true;
    $("#start_play").attr("disabled", "disabled");
    play();
}

/**
 * 回放
 */
function play() {
    if (historyPoint.length === 0) {
        alert("暂无轨迹回放!");
        return false;
    } else {
        historyMarker.setPosition(historyPoint[index]);
        map.setCenter(historyPoint[index]);
        infoWindow.setContent(markerContent[index]);
        infoWindow.open(map, historyMarker);
    }
    index++;
    if (index < historyPoint.length && startFlag === true) {
        var times = $("#range").val();
        window.setTimeout("play()", times);
    } else if (startFlag === true) {
        $("#start_play").removeAttr("disabled");
        setTimeout(function () {
            alert("回放完毕!");
        }, 1000);
        index = 0;
    }
}

/**
 * 更新巡线轨迹
 */
function updateHistory() {
    $.ajax({
        url: "/update_staff_route",
        data: {staffId: staffId, gpsTime: mGpsTime, endTime: Date.parse($("#date_end").val()) / 1000},
        type: "post",
        dataType: "json",

        success: function (json) {
            if (json !== null && json.length > 0) {
                if (updateHistoryMarker.length > 0) {
                    for (var i = 0; i < updateHistoryMarker.length; i++) {
                        updateHistoryMarker[i].setMap(null);
                    }
                    updateHistoryMarker.splice(0, updateHistoryMarker.length);
                }

                if (updateHistoryPolyline !== null) {
                    updateHistoryPoint.splice(0, updateHistoryPoint.length);
                    updateHistoryPolyline.setMap(null);
                }
                for (i = 0; i < json.length; i++) {
                    var data = json[i];
                    var latitude = data.latitude;
                    var longitude = data.longitude;
                    var content = "<div><span style='font-weight: bold;'>纬度坐标: </span>" + latitude + "</div>";
                    content += "<div><span style='font-weight: bold;'>经度坐标: </span>" + longitude + "</div>";
                    var updatePointMarker = new google.maps.Marker({
                        position: new google.maps.LatLng(latitude, longitude),
                        map: map,
                        icon: "/inspection/static/src/img/route_yellow.png"
                    });
                    updateHistoryMarker.push(updatePointMarker);
                    updateHistoryPoint.push(new google.maps.LatLng(latitude, longitude));
                    showInfoWindow(updatePointMarker, content);
                }
                // 画巡线轨迹
                updateHistoryPolyline = new google.maps.Polyline({
                    path: updateHistoryPoint,
                    strokeColor: "#FFFF00",
                    strokeWeight: 5,
                    strokeOpacity: 1
                });
                updateHistoryPolyline.setMap(map);
            }
            window.setTimeout("updateHistory()", 20 * 1000);
        }
    });
}

/**
 * 暂停
 */
function stopPlay() {
    startFlag = false;
    $("#start_play").removeAttr("disabled");
}

/* ********** 谷歌地图的程序入口 **********/
/* 初始化谷歌地图 */
initGoogleMap();
/*****************************************/
