/* 谷歌地图 */
var map = null;
/* 巡线员 id */
var staffId = 0;
/* json 数据 */
var jsonData = null;
/* 覆盖物 */
var pointMarker = [];

/**
 * 初始化谷歌地图
 */
function initGoogleMap() {
    map = new google.maps.Map(document.getElementById("staff_task_detail_map"), {
        zoom: 12,
        center: {lat: 36.9222760000, lng: 119.1296490000},
        mapTypeId: google.maps.MapTypeId.HYBRID
    });

    /* 获取巡线员 id */
    getStaffId();
}

/**
 * 获取巡线员 id
 */
function getStaffId() {
    $.ajax({
        url: "/staff_id",
        data: {},
        dataType: "json",

        success: function (json) {
            if (json !== null) {
                staffId = json.staffId;
                /* 根据坐标画管道 */
                drawPipeline();
                 /* 画必经点 */
                drawStaffTakPoint();
            }
        }
    });
}

/**
 * 画管线
 */
function drawPipeline() {
    $.ajax({
        url: "/staff_pipeline",
        data: {staffId: staffId},
        type: "post",
        dataType: "json",

        success: function (json) {
            if (json !== null && json.length > 0) {
                var linePoint = [];
                for (var i = 0; i < json.length; i++) {
                    var data = json[i];
                    var latitude = data.latitude;
                    var longitude = data.longitude;
                    linePoint.push(new google.maps.LatLng(latitude, longitude))
                }
                // 画管线
                var tmpPolyline = new google.maps.Polyline({
                    path: linePoint,
                    strokeColor: "#0000FF",
                    strokeWeight: 5,
                    strokeOpacity: 1
                });
                tmpPolyline.setMap(map);
            }
        }
    });
}

/**
 * 画巡线员必经点
 */
function drawStaffTakPoint() {
    $.ajax({
        url: "/staff_task_point",
        data: {staffId: staffId},
        type: "post",
        dataType: "json",

        success: function (json) {
            if (json !== null && json.length > 0) {
                jsonData = json;

                // 必经点完成情况
                taskDetail();
            }
        }
    });
}

/**
 * 必经点完成情况
 */
function taskDetail() {
    $.ajax({
        url: "/task_point_complete",
        data: {staffId: staffId},
        type: "post",
        dataType: "json",

        success: function (json) {
            if (json !== null && json.length > 0) {
                var container = document.getElementById("staff_task_point");
                container.innerHTML = "";
                if (pointMarker !== null && pointMarker.length > 0) {
                    for (j = 0; j < pointMarker.length; j++) {
                        pointMarker[j].setMap(null);
                    }
                    pointMarker.splice(0, pointMarker.length);
                }
                for (var i = 0; i < json.length; i++) {

                    var latlng = jsonData[i];
                    var latitude = latlng.latitude;
                    var longitude = latlng.longitude;
                    var icon = "/inspection/static/src/img/route_red.png";

                    var data = json[i];
                    var div = document.createElement("div");
                    if (data.complete) {
                        div.className = "green-circle text-style";
                        icon = "/inspection/static/src/img/route_green.png";
                    } else {
                        div.className = "red-circle text-style";
                        icon = "/inspection/static/src/img/route_red.png";
                    }
                    div.innerHTML = (i + 1);

                    container.appendChild(div);
                    // 画 Marker
                    var staffMarker = new google.maps.Marker({
                        position: new google.maps.LatLng(latitude, longitude),
                        title: latlng.pointName,
                        map: map,
                        icon: icon
                    });

                    pointMarker.push(staffMarker);
                    if (i === Math.round(json.length / 2)) {
                        map.setCenter(staffMarker.getPosition());
                    }
                }
            }
            window.setTimeout("taskDetail()", 20 * 1000);
        }
    });
}

/**
 * 初始化谷歌地图
 */
initGoogleMap();
