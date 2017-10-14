/* Google 地图 */
var map = null;

/**
 * 初始化谷歌地图
 */
function initGoogleMap() {
    map = new google.maps.Map(document.getElementById("repair_map"), {
        zoom: 15,
        center: {lat: 36.9222760000, lng: 119.1296490000},
        mapTypeId: google.maps.MapTypeId.ROADMAP
    });
    var marker = new google.maps.Marker({
        position: {lat: 36.9222760000, lng: 119.1296490000}
    });
    marker.setMap(map);

    // 获取隐患地点
    getDangerAddress();
}

/**
 * 获取隐患地点
 */
function getDangerAddress() {
    $.ajax({
        url: "/repair_map",
        data: {},
        dataType: "json",

        success: function (json) {
            if (json !== null && json.length > 0) {
                var json_length = json.length;
                var marker_array = [];
                for (var i = 0; i < json_length; i++) {
                    var data = json[i];
                    var latitude = data.latitude;
                    var longitude = data.longitude;
                    var staffName = data.staffName;
                    var marker = new google.maps.Marker({
                        position: {lat: latitude, lng: longitude},
                        map: map,
                        title: staffName,
                        icon: "/inspection/static/src/img/blue_01.png"
                    });
                    marker_array.push(marker);
                }
            }
        }
    });
}

/* ********** 谷歌地图的程序入口 **********/
/* 初始化谷歌地图 */
initGoogleMap();
/*****************************************/
