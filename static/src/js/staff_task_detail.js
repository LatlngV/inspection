/* 谷歌地图 */
var map = null;
/* 巡线员 id */
var staffId = 0;

/**
 * 初始化谷歌地图
 */
function initGoogleMap() {
    map = new google.maps.Map(document.getElementById("staff_task_detail_map"), {
        zoom: 13,
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

                // 画必经点
                drawStaffTakPoint();
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
                var pointMarker = [];
                for (var i = 0; i < json.length; i++) {
                    var data = json[i];
                    var latitude = data.latitude;
                    var longitude = data.longitude;
                    // 画 Marker
                    var staffMarker = new google.maps.Marker({
                        position: new google.maps.LatLng(latitude, longitude),
                        map: map,
                        icon: "/inspection/static/src/img/route_red.png"
                    });
                    pointMarker.push(staffMarker);
                }
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
        url: "task_point_complete",
        data: {staffId: staffId},
        type: "post",
        dataType: "json",

        success: function (json) {
            if (json !== null && json.length > 0) {
                var container = document.getElementById("staff_task_point");
                var nodeList = container.childNodes;
                for (var j = nodeList.length; j >= 0; j++) {
                    container.removeChild(nodeList[j]);
                }
                for (var i = 0; i < json.length; i++) {
                    var data = json[i];
                    var div = document.createElement("div");
                    if (data.complete) {
                        div.className = "green-circle";
                    } else {
                        div.className = "red-circle";
                    }
                    div.style.marginTop = "10px";

                    var span = document.createElement("span");
                    span.style.height = "20px";
                    span.style.lineHeight = "20px";
                    span.style.display = "block";
                    span.style.color = "#000000";
                    span.style.textAlign = "center";
                    span.innerHTML = (i + 1);

                    div.appendChild(span);
                    container.appendChild(div);
                }
            }
        }
    });
}

/**
 * 初始化谷歌地图
 */
initGoogleMap();
