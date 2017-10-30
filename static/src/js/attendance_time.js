/* 标志位 */
var flag = 0;
/* 要更新数据的 id */
var updateId = 0;

/**
 * 获取数据
 */
function getAttendanceTime() {
    $.ajax({
        url: "/get_attendance_time",
        data: {},
        dataType: "json",

        success: function (json) {
            if (json !== null && json.length > 0) {
                var tbody = document.getElementById("attendance_body");
                tbody.innerHTML = "";
                for (i = 0; i < json.length; i++) {
                    var data = json[i];
                    var tr = document.createElement("tr");
                    tr.id = data.id;
                    var content = "<td style='vertical-align: middle;'>" + data.attendanceName + "</td>";
                    content += "<td style='vertical-align: middle;'>" + data.startTime + "</td>";
                    content += "<td style='vertical-align: middle;'>" + data.endTime + "</td>";
                    content += "<td style='vertical-align: middle;'>" + data.remark + "</td>";
                    content += "<td><button class='btn btn-info' onclick=\"editAttendanceTime('" + data.id + "','" + data.attendanceName + "','" + data.startTime + "','" + data.endTime + "','" + data.remark + "')\">编辑</button><button style='margin-left: 10px;' class='btn btn-danger' onclick='deleteAttendanceTime(" + data.id + ")'>删除</button></td>";
                    tr.innerHTML = content;
                    tbody.appendChild(tr);
                }
            } else {
                document.getElementById("table").style.display = "none";
                document.getElementById("noData").style.display = "";
            }
        }
    });
}

/**
 * 创建考勤规则
 */
function createAttendanceTime() {
    $(".modal-title").html("创建考勤规则");
    $("#attendance_name").val("");
    $("#start_time").val("");
    $("#end_time").val("");
    $("#remark").val("");
    $("#attendanceTimeModal").modal("show");
    flag = 0;
}

/**
 * 编辑考勤规则
 */
function editAttendanceTime(id, attendanceName, startTime, endTime, remark) {
    $(".modal-title").html("编辑考勤规则");
    $("#attendance_name").val(attendanceName);
    $("#start_time").val(startTime);
    $("#end_time").val(endTime);
    $("#remark").val(remark);
    $("#attendanceTimeModal").modal("show");
    flag = 1;
    updateId = id;
}

/**
 * 删除考勤规则
 */
function deleteAttendanceTime(id) {
    $.ajax({
        url: "/delete_attendance_time",
        data: {"id": id},
        type: "post",
        dataType: "json",

        success: function (json) {
            if (json.message === 0) {
                // 刷新表格
                getAttendanceTime();
            }
        }
    });
}

/**
 * 保存考勤规则
 */
function saveAttendanceTime() {
    if (flag === 0) { // 创建考勤规则，插入到数据库中
        $.ajax({
            url: "/create_attendance_time",
            data: {
                attendanceName: $("#attendance_name").val(),
                startTime: $("#start_time").val(),
                endTime: $("#end_time").val(),
                remark: $("#remark").val()
            },
            type: "post",
            dataType: "json",

            success: function (json) {
                if (json !== null && json.length > 0) {
                    var tbody = document.getElementById("attendance_body");
                    tbody.innerHTML = "";
                    document.getElementById("table").style.display = "";
                    document.getElementById("noData").style.display = "none";
                    for (i = 0; i < json.length; i++) {
                        var data = json[i];
                        var tr = document.createElement("tr");
                        tr.id = data.id;
                        var content = "<td style='vertical-align: middle;'>" + data.attendanceName + "</td>";
                        content += "<td style='vertical-align: middle;'>" + data.startTime + "</td>";
                        content += "<td style='vertical-align: middle;'>" + data.endTime + "</td>";
                        content += "<td style='vertical-align: middle;'>" + data.remark + "</td>";
                        content += "<td><button class='btn btn-info' onclick=\"editAttendanceTime('" + data.id + "','" + data.attendanceName + "','" + data.startTime + "','" + data.endTime + "','" + data.remark + "')\">编辑</button><button style='margin-left: 10px;' class='btn btn-danger' onclick='deleteAttendanceTime(" + data.id + ")'>删除</button></td>";
                        tr.innerHTML = content;
                        tbody.appendChild(tr);
                    }
                    $("#attendanceTimeModal").modal("hide");
                }
            }
        });
    } else if (flag === 1) { // 编辑考勤规则，更新数据库
        $.ajax({
            url: "/update_attendance_time",
            data: {
                id: updateId, attendanceName: $("#attendance_name").val(), startTime: $("#start_time").val(),
                endTime: $("#end_time").val(), remark: $("#remark").val()
            },
            type: "post",
            dataType: "json",

            success: function (json) {
                if (json.message === 0) {
                    var tr = document.getElementById(updateId);
                    tr.childNodes[0].innerHTML = $("#attendance_name").val();
                    tr.childNodes[1].innerHTML = $("#start_time").val();
                    tr.childNodes[2].innerHTML = $("#end_time").val();
                    tr.childNodes[3].innerHTML = $("#remark").val();
                }
                $("#attendanceTimeModal").modal("hide");
            }
        });
    }
}

/**
 * 初始化
 */
getAttendanceTime();
