/* 被选中巡线员的 id */
var select_staff_id = 0;
/* 打开窗口 */
var infoWindow = new google.maps.InfoWindow({});
/* 存储巡线员 marker 的数组 */
var marker_list = [];
/* Google 地图 */
var map = null;

/**
 * 初始化谷歌地图
 */
function initGoogleMap() {
    map = new google.maps.Map(document.getElementById("odoo-google-map"), {
        zoom: 15,
        center: {lat: 36.9222760000, lng: 119.1296490000},
        mapTypeId: google.maps.MapTypeId.ROADMAP
    });
    var marker = new google.maps.Marker({
        position: {lat: 36.9222760000, lng: 119.1296490000}
    });
    marker.setMap(map);

    /* 根据坐标画管道 */
    drawPipeline(map);
    /* 根据坐标显示人员位置 */
    showStaffPosition(0);
    /* 右侧菜单栏展示数据 */
    showRightDrawerData();
}

/**
 * 根据坐标画管道
 */
function drawPipeline(map) {
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
                    // 画管线
                    var tmpPolyline = new google.maps.Polyline({
                        path: line_point,
                        strokeColor: "#0000FF",
                        strokeWeight: 5,
                        strokeOpacity: 1
                    });
                    tmpPolyline.setMap(map);
                }
            }
        },
        error: function () {
            alert("没有获取到相应数据，请检查网络或者刷新重试!");
        }
    });
}

/**
 * 显示信息窗口
 */
function showInfoWindow(map, marker, content, staffId) {
    google.maps.event.addListener(marker, "click", function () {
        map.setCenter(marker.getPosition());
        infoWindow.setContent(content);
        infoWindow.open(map, marker);
        select_staff_id = staffId;
    });
}

/**
 * 显示巡线员位置
 */
function showStaffPosition(flag) {
    $.ajax({
        url: "/staff_position",
        data: {},
        dataType: "json",

        success: function (json) {
            if (json.length > 0 && json !== null) {
                var json_length = json.length;
                var staff_point_list = [];
                if (marker_list.length > 0) {
                    for (var i = 0; i < marker_list.length; i++) {
                        marker_list[i].setMap(null);
                    }
                    marker_list.splice(0, marker_list.length);
                }
                for (var i = 0; i < json_length; i++) {
                    var data = json[i];
                    var latitude = data.latitude;
                    var longitude = data.longitude;
                    var staff_name = data.name;
                    var power = data.power;
                    var speed = data.speed;
                    // 获取巡线员的经纬度坐标
                    staff_point_list.push(new google.maps.LatLng(latitude, longitude));

                    // 根据巡线员的状态显示相应的图标
                    var deviceInfo = data.deviceInfo;
                    var icon = null;
                    if (deviceInfo === 0) { // 设备正常
                        icon = "/inspection/static/src/img/blue_01.png"
                    } else if (deviceInfo === 3) { // 设备离线
                        icon = "/inspection/static/src/img/red_01.png"
                    } else if (data.device_info_new === 4) { // 设备静止
                        icon = "/inspection/static/src/img/black_01.png"
                    } else { // 其他情况
                        icon = "/inspection/static/src/img/yellow_01.png"
                    }

                    // 画 Marker
                    var staff_marker = new google.maps.Marker({
                        position: new google.maps.LatLng(latitude, longitude),
                        map: map,
                        title: staff_name,
                        icon: icon
                    });
                    marker_list.push(staff_marker);

                    // 信息窗口
                    var content = "<div style='font-weight: bold; color: #9d3a3a; font-size: 15px;'>" + staff_name + "</div>";
                    content += "<div><span style='font-weight: bold;'>纬度坐标: </span>" + latitude + "</div>";
                    content += "<div><span style='font-weight: bold;'>经度坐标: </span>" + longitude + "</div>";
                    content += "<div><span style='font-weight: bold;'>速度: </span>" + speed + "</div>";
                    content += "<div><span style='font-weight: bold;'>电量: </span>" + power + "</div>";
                    content += "<div style='margin-top: 3px;'><span><a href='/loading/google_map?flag=patrol_track&staff_id=" + select_staff_id + "'" + ">轨迹回放</a></span></div>";

                    showInfoWindow(map, staff_marker, content, data.staff_id);
                    if (select_staff_id === data.staff_id) {
                        infoWindow.setContent(content);
                        infoWindow.open(map, staff_marker);
                        if (flag === 1) {
                            map.setCenter(staff_marker.getPosition());
                        }
                    }
                }
                window.setTimeout("showStaffPosition(1)", 20 * 1000);
            } else {
                alert("当前没有员工可以显示!");
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
            $('#tree').treeview({
                data: json,

                onNodeSelected: function (event, node) {
                    select_staff_id = node.staff_id;
                    /* 显示巡线员位置 */
                    showStaffPosition(1);
                },
                onNodeUnselected: function () {
                    select_staff_id = 0;
                }
            });
        }
    });
}

/* ********** 谷歌地图的程序入口 **********/
/* 初始化谷歌地图 */  /********************/
initGoogleMap();     /********************/
/*****************************************/
