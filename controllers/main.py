# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
from odoo.exceptions import ValidationError
import json
import time
from datetime import datetime
import calendar
from math import radians, cos, sin, asin, sqrt


class GoogleMap(http.Controller):
    """
        谷歌地图
    """

    @http.route("/loading/google_map", type="http", auth="public", website=True)
    def loading_google_map(self, **kwargs):
        """
            渲染谷歌地图
        """
        flag = kwargs.get("flag", "")
        staff_id = kwargs.get("staff_id", 0)

        values = {
            "partner_url": "partner_url",
            "partner_data": "partner_data",
            "flag": flag,
            "staff_id": staff_id
        }
        if flag == "loading_google_map":  # 巡线员实时位置
            return request.render("inspection.loading_google_map", values)
        elif flag == "patrol_track":  # 巡线员巡检轨迹
            return request.render("inspection.dotop_patrol_track", values)
        elif flag == "staff_report":  # 巡线员报表
            return request.render("inspection.dotop_staff_report", values)
        elif flag == "repair_map":  # 维修工人维修地图
            return request.render("inspection.repair_map", values)
        elif flag == "staff_task_detail":  # 巡线员任务详情
            return request.render("inspection.dotop_staff_task_detail", values)
        elif flag == "attendance_time":  # 考勤规则
            return request.render("inspection.dotop_attendance_time", values)


class MapOptions(http.Controller):
    """
        操作地图
    """

    @http.route("/staff_line", type="http", auth="public", website=True, csrf=False)
    def staff_line(self):
        """
        返回所有巡线点
        """
        sections = request.env["inspection.patrol_section"].search([])
        section_list = []
        for section in sections:
            """
            添加巡线段
            """
            section_dict = {"id": str(section.id),
                            "belong_area": str(section.belong_area.name),
                            "area_name": str(section.area_name),
                            "patrol_employee": str(section.patrol_employee.id),
                            "latlng": []}
            points = request.env["inspection.patrol_point"].search([("belong_section.id", "=", section.id)])

            point_list = section_dict["latlng"]
            for point in points:
                """
                    根据巡线段添加巡线点
                """
                point_dict = {"id": str(point.id),
                              "name": str(point.point_name),
                              "latitude": str(point.latitude),
                              "longitude": str(point.longitude)}
                point_list.append(point_dict)

            section_list.append(section_dict)
        return json.dumps(section_list)

    @http.route("/staff_position", type="http", auth="public", website=True, csrf=False)
    def staff_position(self):
        """
        获取巡线员位置
        """
        gps_managers = request.env["inspection.gps_manager"].search([])
        staff_position_list = []
        for gps_manager in gps_managers:
            if gps_manager.staff:
                staff_position_dict = {"name": gps_manager.name, "latitude": gps_manager.latitude,
                                       "longitude": gps_manager.longitude, "speed": gps_manager.speed,
                                       "power": gps_manager.power, "deviceInfo": gps_manager.device_info,
                                       "device_info_new": gps_manager.device_info_new, "staff_id": gps_manager.staff.id}
                staff_position_list.append(staff_position_dict)
        return json.dumps(staff_position_list)

    @http.route("/show_all_employees", type="http", auth="public", website=True, csrf=False)
    def show_all_employees(self):
        """
        根据分班情况将人员添加进去
        这里用的 treeview 这个组件，需要用特定的 json 格式
        """
        patrol_areas = request.env["hr.department"].search([("patrol_department", "=", True)])
        patrol_area_list = []
        for patrol_area in patrol_areas:
            staffs = request.env["hr.employee"].search(
                [("department_id", "=", patrol_area.id), ("select_job", "=", "patrol_employee")])
            if len(staffs) > 0:
                index = 0
                gps_manager = request.env["inspection.gps_manager"].search(
                    [("staff.department_id", "=", patrol_area.id)])
                for record in gps_manager:
                    if record.device_info == 0:
                        index += 1
                patrol_area_dict = {"text": str(patrol_area.name) + " (" + str(index) + "/" + str(len(staffs)) + ")",
                                    "selectable": False, "nodes": []}
                for staff in staffs:
                    name = staff.name_related
                    gps_manager = request.env["inspection.gps_manager"].search([("staff", "=", staff.id)])
                    if gps_manager.device_info == 0:
                        color = "#000000"
                        text = name + " (设备正常)"
                    elif gps_manager.device_info == 1:
                        color = "#DAA520"
                        text = name + " (设备未上线)"
                    elif gps_manager.device_info == 2:
                        color = "#D3D3D3"
                        text = name + " (设备已过期)"
                    elif gps_manager.device_info == 3:
                        color = "#FF0000"
                        text = name + " (设备离线)"
                    elif gps_manager.device_info_new == 4:
                        color = "#ccc"
                        text = name + " (设备静止)"
                    staff_dict = {"text": text, "staff_id": staff.id, "icon": "glyphicon glyphicon-user",
                                  "color": color}
                    patrol_area_dict["nodes"].append(staff_dict)
                patrol_area_list.append(patrol_area_dict)
        return json.dumps(patrol_area_list)

    @http.route("/show_track", type="http", auth="public", website=True, csrf=False)
    def show_track(self, **kwargs):
        """
        巡检轨迹
        """
        staff_id = kwargs.get("staff_id", 1)
        begin_time = kwargs.get("begin_time", "")
        end_time = kwargs.get("end_time", "")
        table_name_time = str(begin_time)[0: 7].split("-")
        table_name = "dotop_" + table_name_time[0] + table_name_time[1]
        if begin_time != 0 and end_time != 0:
            begin_time_array = time.strptime(begin_time, "%Y-%m-%d %H:%M:%S")
            begin_time = int(time.mktime(begin_time_array)) - 8 * 60 * 60
            end_time_array = time.strptime(end_time, "%Y-%m-%d %H:%M:%S")
            end_time = int(time.mktime(end_time_array)) - 8 * 60 * 60
        staff_track_list = []
        staff_track_sql = """SELECT staff_id, latitude, longitude, imei, speed, gps_time FROM %s WHERE staff_id=%s AND gps_time>=%s AND gps_time<=%s ORDER BY gps_time ASC""" % (
            table_name, staff_id, begin_time, end_time)
        request.env.cr.execute(staff_track_sql)
        for (staff_id, latitude, longitude, imei, speed, gps_time) in request.env.cr.fetchall():
            staff = request.env["hr.employee"].search([("id", "=", staff_id)])[0].name_related
            staff_track_dict = {"staff": staff, "latitude": latitude, "longitude": longitude, "imei": imei,
                                "speed": speed, "gps_time": gps_time}
            staff_track_list.append(staff_track_dict)
        return json.dumps(staff_track_list)

    @http.route("/skip/patrol_track", type="http", auth="public", website=True, csrf=False)
    def skip_patrol_track(self):
        """
        跳转到轨迹回放
        """
        response = {"response": "Success"}
        return json.dumps(response)

    @http.route("/line_position", type="http", auth="public", website=True, csrf=False)
    def line_position(self, **kwargs):
        """
        根据巡线员 id 获取其相应的管线数据
        """
        staff_id = kwargs.get("staff_id", 1)
        if staff_id:
            patrol_section = request.env["inspection.patrol_section"].search([("patrol_employee.id", "=", staff_id)])
            patrol_points = request.env["inspection.patrol_point"].search(
                [("belong_section.id", "=", patrol_section.id)])
            patrol_point_dict = {"line_id": str(patrol_section.id), "point_list": []}
            for point in patrol_points:
                point_dict = {"id": str(point.id),
                              "name": str(point.point_name),
                              "latitude": str(point.latitude),
                              "longitude": str(point.longitude)}
                patrol_point_dict["point_list"].append(point_dict)
            return json.dumps(patrol_point_dict)
        else:
            raise ValidationError(u"没有找到该员工")

    @http.route("/show_button", type="http", auth="public", website=True, csrf=False)
    def show_button(self):
        """
        根据 button 显示考勤时间的数据
        """
        attendance_times = request.env["inspection.attendance_time"].search([])
        attendance_time_list = []
        for attendance_time in attendance_times:
            date = datetime.now()
            start_time_list = str(attendance_time.start_time).split(".")
            end_time_list = str(attendance_time.end_time).split(".")
            start_second = ""
            end_second = ""
            if start_time_list[1]:
                start_second = str(int(float(start_time_list[1]) * 0.6))
                if len(start_second) == 1:
                    start_second += "0"
            if end_time_list[1]:
                end_second = str(int(float(end_time_list[1]) * 0.6))
                if len(end_second) == 1:
                    end_second += "0"
            start_time = str(date.year) + "-" + str(date.month) + "-" + str(date.day) + " " + str(
                start_time_list[0]) + ":" + start_second + ":00"
            end_time = str(date.year) + "-" + str(date.month) + "-" + str(date.day) + " " + str(
                end_time_list[0]) + ":" + end_second + ":00"
            if attendance_time.end_time < attendance_time.start_time:
                time_array = time.strptime(end_time, "%Y-%m-%d %H:%M:%S")
                time_stamp = int(time.mktime(time_array)) + 24 * 60 * 60
                time.localtime(time_stamp)
                end_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time_stamp))
            attendance_time_dict = {"attendance_id": attendance_time.id, "attendance_name": attendance_time.name,
                                    "attendance_start_time": start_time, "attendance_end_time": end_time}
            attendance_time_list.append(attendance_time_dict)
        return json.dumps(attendance_time_list)

    @http.route("/staff_department", type="http", auth="public", website=True, csrf=False)
    def staff_department(self):
        """
        巡线员部门
        """
        departments = request.env["hr.department"].search([("patrol_department", "=", True)])
        department_list = []
        for department in departments:
            department_dict = {"departmentId": department.id, "departmentName": department.name}
            department_list.append(department_dict)
        return json.dumps(department_list)

    @http.route("/staff_report", type="http", auth="public", website=True, csrf=False)
    def staff_report(self, **kwargs):
        """
        巡线员报表
        :return json 数据
        """
        department_id = kwargs.get("departmentId", 1)
        report_type = kwargs.get("reportType", 1)
        date = kwargs.get("date", "2017-10-20")

        start_date_stamp = 0
        end_date_stamp = 0
        if report_type == "1":  # 日报表
            start_date_stamp = self.date2timeStamp(date)
            end_date_stamp = start_date_stamp + 24 * 60 * 60
        elif report_type == "2":  # 月报表
            month = date.split("-")[1]
            year = date.split("-")[0]

            # 如果当前月份是十二月份，
            if int(month) == 12:
                year = str(int(year) + 1)
                month = "-01"
            else:
                month = str(int(month) + 1)
                if len(month) == 1:
                    month = "-0" + month
                else:
                    month = "-" + month
            start_date = date + "-01"
            end_date = year + month + "-01"
            start_date_stamp = self.date2timeStamp(start_date)
            end_date_stamp = self.date2timeStamp(end_date)
        elif report_type == "3":  # 年报表
            start_date = date + "-01-01"
            end_date = str(int(date) + 1) + "-01-01"
            start_date_stamp = self.date2timeStamp(start_date)
            end_date_stamp = self.date2timeStamp(end_date)
        staffs = request.env["hr.employee"].search([("department_id.id", "=", department_id)])
        data_list = []

        for staff in staffs:
            # 计算有效范围内的必经点
            request.env.cr.execute(
                """SELECT default_range, one_hundred_range, two_hundred_range, five_hundred_range, thousand_range, id FROM staff_task_detail WHERE staff_id=%s AND create_time>=%s AND create_time < %s""" % (
                    staff.id, start_date_stamp, end_date_stamp))
            default_count = 0
            one_hundred_count = 0
            two_hundred_count = 0
            five_hundred_count = 0
            thousand_count = 0

            for report in request.env.cr.fetchall():
                if report[0]:
                    default_count += 1
                if report[1]:
                    one_hundred_count += 1
                if report[2]:
                    two_hundred_count += 1
                if report[3]:
                    five_hundred_count += 1
                if report[4]:
                    thousand_count += 1

            # 计算必经点总数
            query = """SELECT point_count FROM staff_task WHERE staff_id=%s AND create_time>=%s AND create_time<=%s"""
            request.env.cr.execute(query, (staff.id, start_date_stamp, end_date_stamp))
            total_point_count = 0
            for row in request.env.cr.fetchall():
                total_point_count += row[0]

            # 获取管线长度
            pipeline_length = 0
            patrol_sections = request.env["inspection.patrol_section"].search([("patrol_employee.id", "=", staff.id)])
            for patrol_section in patrol_sections:
                pipeline_length = patrol_section.pipeline_length

            # 巡线员必经点数量
            staff_points = request.env["inspection.staff_point"].search([("belong_staff.id", "=", staff.id)])

            # 计算里程
            days = 0
            total_kilo = 0
            current_date = None
            if report_type == "1":
                days = 1
                current_date = str(date)
            elif report_type == "2":
                date_list = date.split("-")
                date_tuple = calendar.monthrange(int(date_list[0]), int(date_list[1]))
                days = date_tuple[1]
                current_date = str(date) + "-01"
            elif report_type == "3":
                if int(date) % 4 == 0:
                    days = 366
                else:
                    days = 365
                current_date = str(date) + "-01-01"
            for i in range(0, days):
                attendance_times = request.env["inspection.attendance_time"].search([])
                for attendance_time in attendance_times:
                    begin_time_stamp = self._time_stamp(current_date, attendance_time.start_time)
                    stop_time_stamp = self._time_stamp(current_date, attendance_time.end_time)
                    date_array = current_date.split("-")
                    table_name = "dotop_" + date_array[0] + date_array[1]
                    table_query = """SELECT tablename FROM pg_tables"""
                    request.env.cr.execute(table_query)
                    for row in request.env.cr.fetchall():
                        if row[0] is not None and row[0] == table_name:
                            history_query = """SELECT latitude, longitude FROM %s WHERE staff_id=%s AND gps_time>=%s AND gps_time<=%s""" % (
                                table_name, staff.id, begin_time_stamp, stop_time_stamp)
                            request.env.cr.execute(history_query)

                            index = 0  # 开始的标志位，如果是 0 就给临时变量赋值
                            temp_latitude = 0  # 纬度坐标的临时变量
                            temp_longitude = 0  # 经度坐标的临时变量
                            for record in request.env.cr.fetchall():
                                if index == 0:
                                    temp_latitude = record[0]
                                    temp_longitude = record[1]
                                    index = 1
                                else:
                                    distance = self._haversine(temp_longitude, temp_latitude, record[1], record[0])
                                    total_kilo += distance

                                    # 重新给经纬度坐标的临时变量赋值
                                    temp_latitude = record[0]
                                    temp_longitude = record[1]

                time_array = time.strptime(str(current_date), "%Y-%m-%d")
                time_stamp = int(time.mktime(time_array)) + 24 * 60 * 60
                time_arrays = time.localtime(time_stamp)
                current_date = time.strftime("%Y-%m-%d", time_arrays)

            # 将数据添加到字典中，将字典添加到列表中
            data_list.append({"totalPoint": total_point_count, "defaultCount": default_count,
                              "oneHundredCount": one_hundred_count, "twoHundredCount": two_hundred_count,
                              "fiveHundredCount": five_hundred_count, "thousandCount": thousand_count,
                              "staffName": staff.name_related, "pipelineLength": pipeline_length,
                              "department": staff.department_id.name, "pointCount": len(staff_points),
                              "staffId": staff.id, "totalKilo": round(total_kilo, 2)})
        return json.dumps(data_list)

    def _haversine(self, longitude1, latitude1, longitude2, latitude2):
        """
        在球上计算两点之间的距离(haversine 公式)
        """
        # 将十进制度数转化为弧度
        list = map(radians, [longitude1, latitude1, longitude2, latitude2])

        # haversine 公式
        distance_longitude = list[2] - list[0]
        distance_latitude = list[3] - list[1]
        a = sin(distance_latitude / 2) ** 2 + cos(list[1]) * cos(list[3]) * sin(distance_longitude / 2) ** 2
        c = 2 * asin(sqrt(a))
        # 地球平均半径，单位为公里
        r = 6371
        return c * r

    def _time_stamp(self, date, float_time):
        """
        拼接时间转换成时间戳
        :param date: 日期（年月日，不包含时分秒）
        :param float_time: 将 float 类型的数字转换为时间
        :return: 时间戳
        """
        time_list = str(float_time).split(".")
        minutes = time_list[1]
        if minutes != 0:
            if len(minutes) == 1:
                minutes = minutes + "0"
            minutes = str(int(float(minutes) * 3 / 5))
        date = date + " " + time_list[0] + ":" + minutes + ":00"
        time_array = time.strptime(date, "%Y-%m-%d %H:%M:%S")
        time_stamp = int(time.mktime(time_array))
        return time_stamp

    def date2timeStamp(self, date):
        """
        将日期转换为时间戳
        :param date: 日期
        :return: 时间戳
        """
        date = date + " 00:00:00"
        time_array = time.strptime(date, "%Y-%m-%d %H:%M:%S")
        time_stamp = int(time.mktime(time_array))
        return time_stamp

    @http.route("/staff_point", type="http", auth="public", website=True, csrf=False)
    def staff_point(self):
        """
        巡线员的必经点
        :return: json 数据
        """
        staff_points = request.env["inspection.staff_point"].search([])
        point_list = []
        for staff_point in staff_points:
            point_dict = {"id": str(staff_point.id), "pointName": str(staff_point.staff_point_name),
                          "latitude": str(staff_point.latitude), "longitude": str(staff_point.longitude)}
            point_list.append(point_dict)
        return json.dumps(point_list)

    @http.route("/repair_map", type="http", auth="public", website=True, csrf=False)
    def repair_map(self):
        """
        维修地图
        :return json 数据
        """
        user_id = request.uid
        repair_staffs = request.env["hr.employee"].search([("resource_id.user_id.id", "=", user_id)])
        for repair_staff in repair_staffs:
            repair_staff_id = repair_staff.id
            repair_managers = request.env["inspection.repair_manager"].search(
                [("repair_employee.id", "=", repair_staff_id), ("state", "=", "processing")])
            danger_point_list = []
            for repair_manager in repair_managers:
                latitude = repair_manager.latitude
                longitude = repair_manager.longitude
                staff = repair_manager.find_employee.name_related
                request.env.cr.execute(
                    """SELECT res_id FROM ir_attachment WHERE res_model='inspection.danger_category'""")
                for row in request.env.cr.fetchall():
                    if row[0] is not None:
                        danger_point_dict = {"latitude": latitude, "longitude": longitude, "staffName": staff,
                                             "icon": row[0]}
                danger_point_list.append(danger_point_dict)
            return json.dumps(danger_point_list)

    @http.route("/task_detail", type="http", auth="public", website=True, csrf=False)
    def task_detail(self, **kwargs):
        """
        根据员工 id 选择巡线员的数据
        :return json 数据
        [
            {"pointName": 值, "latlng": 值, "morning": 值, "afternoon": 值},
            {"pointName": 值, "latlng": 值, "morning": 值, "afternoon": 值},
        ]
        """
        staff_id = kwargs.get("staffId", 0)
        date = kwargs.get("date", "2017-10-18")
        range_flag = int(kwargs.get("rangeFlag", 0))

        staff_points = request.env["inspection.staff_point"].search([("belong_staff.id", "=", staff_id)])
        data_list = []
        for staff_point in staff_points:
            latlng = str(staff_point.latitude) + "," + str(staff_point.longitude)
            data_dict = {"pointName": staff_point.staff_point_name, "latlng": latlng}

            start_date = str(date) + " 00:00:00"
            time_array = time.strptime(start_date, "%Y-%m-%d %H:%M:%S")
            end_time_stamp = int(time.mktime(time_array)) + 24 * 60 * 60
            start_time_stamp = int(time.mktime(time_array))
            task_query = """SELECT id FROM staff_task WHERE staff_id=%s AND create_time>=%s AND create_time<%s"""
            request.env.cr.execute(task_query, (staff_id, start_time_stamp, end_time_stamp))
            for record in request.env.cr.fetchall():
                task_detail_query = ""
                if range_flag == 1:
                    task_detail_query = """SELECT default_range FROM staff_task_detail WHERE task_id=%s"""
                if range_flag == 2:
                    task_detail_query = """SELECT one_hundred_range FROM staff_task_detail WHERE task_id=%s"""
                if range_flag == 3:
                    task_detail_query = """SELECT two_hundred_range FROM staff_task_detail WHERE task_id=%s"""
                if range_flag == 4:
                    task_detail_query = """SELECT five_hundred_range FROM staff_task_detail WHERE task_id=%s"""
                if range_flag == 5:
                    task_detail_query = """SELECT thousand_range FROM staff_task_detail WHERE task_id=%s"""

                request.env.cr.execute(task_detail_query, (record[0],))
                for row in request.env.cr.fetchall():
                    if row[0]:
                        data_dict["morning"] = "0"
                    else:
                        data_dict["afternoon"] = "1"
            data_list.append(data_dict)
        return json.dumps(data_list)

    @http.route("/save_staff_point", type="http", auth="public", website=True, csrf=False)
    def save_staff_point(self, **kwargs):
        """
        保存必经点
        """
        staff_id = kwargs.get("staffId", 0)
        point_name = kwargs.get("pointName", "")
        latitude = kwargs.get("latitude", 0)
        longitude = kwargs.get("longitude", 0)
        attendance_range = kwargs.get("attendanceRange", 0)

        if staff_id != 0 and point_name != "" and attendance_range > 0:
            staff_point = request.env["inspection.staff_point"]
            staff_point.create({"latitude": latitude, "longitude": longitude, "belong_staff": staff_id,
                                "staff_point_name": point_name, "attendance_range": attendance_range,
                                "create_date": datetime.now()})
            return json.dumps({"response": "success"})
        else:
            return json.dumps({"response": u"请填写正确的必经点信息"})

    @http.route("/staff_id", type="http", auth="public", website=True, csrf=False)
    def staff_id(self):
        """
        获取当前用户在 hr_employee 表中的 id
        :return: 员工表中的 id
        {"staffId": 1}
        """
        user_id = request._uid
        staffs = request.env["hr.employee"].search([("resource_id.user_id.id", "=", user_id)])
        for staff in staffs:
            return json.dumps({"staffId": staff.id})

    @http.route("/staff_pipeline", type="http", auth="public", website=True, csrf=False)
    def staff_pipeline(self, **kwargs):
        """
        根据巡线员获取对应管线数据
        :param kwargs: post 过来的参数
        :return: 管线数据的 json
        [
            {"latitude": 35, "longitude": 120}, {"latitude": 35, "longitude": 120}, ...
        ]
        """
        staff_id = kwargs.get("staffId", 0)
        if staff_id != 0:
            patrol_sections = request.env["inspection.patrol_section"].search([("patrol_employee.id", "=", staff_id)])
            point_list = []
            for patrol_section in patrol_sections:
                points = request.env["inspection.patrol_point"].search([("belong_section.id", "=", patrol_section.id)])
                for point in points:
                    point_dict = {"latitude": point.latitude, "longitude": point.longitude}
                    point_list.append(point_dict)
            return json.dumps(point_list)

    @http.route("/staff_task_point", type="http", auth="public", website=True, csrf=False)
    def staff_task_point(self, **kwargs):
        """
        巡线员的必经点
        :param kwargs: post 过来的参数
        :return: 巡线员的任务点
        [
            {"pointName": "xxx", "latitude": 35, "longitude": 120},
            {"pointName": "xxx", "latitude": 35, "longitude": 120}, ...
        ]
        """
        staff_id = kwargs.get("staffId", 0)
        if staff_id != 0:
            staff_points = request.env["inspection.staff_point"].search([("belong_staff.id", "=", staff_id)])
            point_list = []
            for staff_point in staff_points:
                point_dict = {"pointName": staff_point.staff_point_name, "latitude": staff_point.latitude,
                              "longitude": staff_point.longitude}
                point_list.append(point_dict)
            return json.dumps(point_list)

    @http.route("/task_point_complete", type="http", auth="public", website=True, csrf=False)
    def task_point_complete(self, **kwargs):
        """
        任务点完成情况
        :return: 完成情况的 json
        [
            {"complete": True}, {"complete": False}, ...
        ]
        """
        staff_id = kwargs.get("staffId", 0)

        time_stamp = int(time.time())
        current_date = time.strftime("%Y-%m-%d", time.localtime(time.time()))
        attendance_times = request.env["inspection.attendance_time"].search([])
        task_detail_list = []
        for attendance_time in attendance_times:
            start_time_stamp = self._time_stamp(current_date, attendance_time.start_time) - 8 * 60 * 60
            end_time_stamp = self._time_stamp(current_date, attendance_time.end_time) - 8 * 60 * 60

            if time_stamp in range(start_time_stamp, end_time_stamp):
                staff_points = request.env["inspection.staff_point"].search([("belong_staff.id", "=", staff_id)])

                for staff_point in staff_points:
                    query = """SELECT latitude, longitude FROM dotop_staff_position WHERE staff_id=%s AND gps_time>=%s AND gps_time<=%s"""
                    request.env.cr.execute(query, (staff_id, start_time_stamp, end_time_stamp))
                    task_detail_dict = {}
                    for row in request.env.cr.fetchall():
                        distance = self._haversine(row[1], row[0], staff_point.longitude, staff_point.latitude) * 1000
                        if distance <= 1000:
                            task_detail_dict["complete"] = True
                            break
                        else:
                            task_detail_dict["complete"] = False
                    staff_point.write({"complete": task_detail_dict["complete"]})  # 将状态保存到数据库中
                    task_detail_list.append(task_detail_dict)
        # 如果列表为空，从数据库中读取状态
        if len(task_detail_list) == 0:
            staff_points = request.env["inspection.staff_point"].search([("belong_staff.id", "=", staff_id)])
            for staff_point in staff_points:
                task_detail_dict = {"complete": staff_point.complete}
                task_detail_list.append(task_detail_dict)
        return json.dumps(task_detail_list)

    @http.route("/update_staff_route", type="http", auth="public", website=True, csrf=False)
    def update_staff_route(self, **kwargs):
        """
        更新巡线员巡线轨迹
        :param kwargs: 必要参数
        :return: 更新后的巡线轨迹
        """
        staff_id = int(kwargs.get("staffId", 0))
        gps_time = int(kwargs.get("gpsTime", 0))
        end_time = int(kwargs.get("endTime", ""))

        update_history_list = []
        if gps_time < end_time:
            query = """SELECT latitude, longitude FROM dotop_staff_position WHERE staff_id=%s AND gps_time>%s AND gps_time<=%s ORDER BY gps_time DESC"""
            request.env.cr.execute(query, (staff_id, gps_time, end_time))
            for record in request.env.cr.fetchall():
                update_history_dict = {"latitude": record[0], "longitude": record[1]}
                update_history_list.append(update_history_dict)
            return json.dumps(update_history_list)
        else:
            return json.dumps(update_history_list)

    @http.route("/get_attendance_time", type="http", auth="public", website=True, csrf=False)
    def get_attendance_time(self):
        """
        获取考勤规则
        :return:
        """
        query = """SELECT * FROM dotop_attendance_time ORDER BY id DESC """
        request.env.cr.execute(query)
        attendance_time_list = []
        for record in request.env.cr.fetchall():
            attendance_time_dict = {"id": record[0], "attendanceName": record[1], "startTime": record[2],
                                    "endTime": record[3], "remark": record[4]}
            attendance_time_list.append(attendance_time_dict)
        return json.dumps(attendance_time_list)

    @http.route("/create_attendance_time", type="http", auth="public", website=True, csrf=False)
    def create_attendance_time(self, **kwargs):
        """
        创建考勤规则
        :param kwargs: post 过来的参数
        :return:
        """
        attendance_name = kwargs.get("attendanceName", "")
        start_time = kwargs.get("startTime", "")
        end_time = kwargs.get("endTime", "")
        remark = kwargs.get("remark", "")

        insert = """INSERT INTO dotop_attendance_time (attendance_name, start_time, end_time, remark) VALUES (%s, %s, %s, %s)"""
        request.env.cr.execute(insert, (attendance_name, start_time, end_time, remark))

        query = """SELECT * FROM dotop_attendance_time"""
        request.env.cr.execute(query)
        attendance_time_list = []
        for record in request.env.cr.fetchall():
            attendance_time_dict = {"id": record[0], "attendanceName": record[1], "startTime": record[2],
                                    "endTime": record[3], "remark": record[4]}
            attendance_time_list.append(attendance_time_dict)
        return json.dumps(attendance_time_list)

    @http.route("/update_attendance_time", type="http", auth="public", website=True, csrf=False)
    def update_attendance_time(self, **kwargs):
        """
        更新数据
        :param kwargs: post 过来的参数
        :return:
        """
        id = kwargs.get("id", 0)
        attendance_name = kwargs.get("attendanceName", 0)
        start_time = kwargs.get("startTime", 0)
        end_time = kwargs.get("endTime", 0)
        remark = kwargs.get("remark", 0)

        update = """UPDATE dotop_attendance_time SET attendance_name=%s, start_time=%s, end_time=%s, remark=%s WHERE id=%s"""
        request.env.cr.execute(update, (attendance_name, start_time, end_time, remark, id))

        return json.dumps({"message": 0})

    @http.route("/delete_attendance_time", type="http", auth="public", website=True, csrf=False)
    def delete_attendance_time(self, **kwargs):
        """
        删除数据
        :param kwargs: post 过来的参数
        :return:
        """
        id = kwargs.get("id", 0)

        delete = """DELETE FROM dotop_attendance_time WHERE id=%s"""
        request.env.cr.execute(delete, (id,))
        return json.dumps({"message": 0})
