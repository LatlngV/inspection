# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
from odoo.exceptions import ValidationError
import json
import time
from datetime import datetime


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
        if flag == "loading_google_map":
            return request.render("inspection.loading_google_map", values)
        elif flag == "patrol_track":
            return request.render("inspection.dotop_patrol_track", values)
        elif flag == "repair_map":
            return request.render("inspection.repair_map", values)


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
            if gps_manager.staff and gps_manager.staff is not None:
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
        staff_track_sql = """SELECT staff_id, latitude, longitude, imei, speed, gps_time FROM %s WHERE staff_id = '%s' AND gps_time > '%s' AND gps_time < '%s'""" % (
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


class Report(http.Controller):
    """
    报表
    """

    @http.route("/staff_department", type="http", auth="public", website=True, csrf=False)
    def staff_department(self):
        """
        巡线员部门
        """
        departments = request.env["hr.department"].search([])
        department_list = []
        for department in departments:
            department_dict = {"departmentId": department.id, "departmentName": department.name}
            department_list.append(department_dict)
        return json.dumps(department_list)

    @http.route("/staff_report", type="http", auth="public", website=True, csrf=False)
    def staff_route(self, **kwargs):
        """
        巡线员报表
        """
        department_id = kwargs.get("departmentId", 1)
        report_type = kwargs.get("reportType", 1)
        date = kwargs.get("date", "")
        start_date_stamp = 0
        end_date_stamp = 0
        if report_type == 1:  # 日报表
            start_date_stamp = self.date2timeStamp(date)
            end_date_stamp = start_date_stamp + 24 * 60 * 60
        elif report_type == 2:  # 月报表
            month = date.split("-")[1]
            year = date.split("-")[0]

            # 如果当前月份是十二月份，
            if int(month) == 12:
                year = str(int(year) + 1)
                month = "-01"
            else:
                month = str(int(month) + 1)
                if len(month) == 1:
                    month = "0" + month
            start_date = date + "-01"
            end_date = year + month + "-01"
            start_date_stamp = self.date2timeStamp(start_date)
            end_date_stamp = self.date2timeStamp(end_date)
        elif report_type == 3:  # 年报表
            start_date = date + "-01-01"
            end_date = str(int(date) + 1) + "-01-01"
            start_date_stamp = self.date2timeStamp(start_date)
            end_date_stamp = self.date2timeStamp(end_date)
        staffs = request.env["hr.employee"].search([("department_id", "=", department_id)])
        data_list = []
        for staff in staffs:
            request.env.cr.execute(
                """SELECT default_range, one_hundred_range, two_hundred_range, five_hundred_range, thousand_range FROM staff_task_detail WHERE staff_id=%s AND create_time>=%s AND create_time<%s""" % (
                    staff.id, str(start_date_stamp), str(end_date_stamp)))
            default_count = 0
            one_hundred_count = 0
            two_hundred_count = 0
            five_hundred_count = 0
            thousand_count = 0
            for year_report in request.env.cr.fetchall():
                if year_report[0]:
                    default_count += 1
                if year_report[1]:
                    one_hundred_count += 1
                if year_report[2]:
                    two_hundred_count += 1
                if year_report[3]:
                    five_hundred_count += 1
                if year_report[4]:
                    thousand_count += 1
            # 计算必经点总数
            request.env.cr.execute(
                """SELECT point_count FROM staff_task_detail WHERE staff_id=%s AND create_time>=%s AND create_time<=%s""" % (
                    staff.id, str(start_date_stamp), str(end_date_stamp)))
            total_point_count = 0
            for row in request.env.cr.fetchall():
                total_point_count += row[0]
            data_list.append({"totalPoint": total_point_count, "defaultCount": default_count,
                              "oneHundredCount": one_hundred_count, "twoHundredCount": two_hundred_count,
                              "fiveHundredCount": five_hundred_count, "thousandCount": thousand_count})
        return json.dumps(data_list)

    def date2timeStamp(self, date):
        """
        将日期转换为时间戳
        :param date: 日期
        :return: 时间戳
        """
        time_array = time.strptime(date, "%Y-%m-%d %H:%M:%S")
        time_stamp = int(time.mktime(time_array))
        return time_stamp

    @http.route("/staff_point", type="http", auth="public", website=True, csrf=False)
    def staff_point(self):
        staff_points = request.env["inspection.staff_point"].search([])
        point_list = []
        for staff_point in staff_points:
            point_dict = {"id": str(staff_point.id), "pointName": str(staff_point.staff_point_name),
                          "latitude": str(staff_point.latitude), "longitude": str(staff_point.longitude)}
            point_list.append(point_dict)
        return json.dumps(point_list)

    @http.route("/repair_map", type="http", auth="public", website=True, csrf=False)
    def repair_map(self):
        user_id = request.session.db
        print user_id
        repair_staffs = request.env["hr.employee"].search([("recourse_id.id", "=", user_id)])
        for repair_staff in repair_staffs:
            repair_staff_id = repair_staff.id
            repair_managers = request.env["inspection.repair_manager"].search(
                [("repair_employee.id", "=", repair_staff_id), ("state", "=", "processing")])
            danger_point_list = []
            for repair_manager in repair_managers:
                latitude = repair_manager.latitude
                longitude = repair_manager.longitude
                staff = repair_manager.find_employee.name_related
                danger_point_dict = {"latitude": latitude, "longitude": longitude, "staffName": staff}
                danger_point_list.append(danger_point_dict)
            return json.dumps(danger_point_list)


"""
color_list = ["#FF0000", "#00FF00", "#0000FF", "#00FFFF", "#FF00FF", "#FFFF00"]
for patrol_area in patrol_areas:
    patrol_area_dict = {}
    patrol_area_dict["text"] = str(patrol_area.name)
    patrol_area_dict["selectable"] = False
    patrol_area_dict["nodes"] = []

    times = request.env["inspection.attendance_time"].search([])
    index = 0
    for time in times:
        patrol_area_dict["nodes"].append(
            {"text": str(time.name), "time_id": str(time.id), "selectable": False, "color": color_list[index],
             "nodes": []})
        for employee in time.employee_id:
            if employee.department_id.id == patrol_area.id:
                patrol_area_dict["nodes"][index]["nodes"].append({
                    "text": employee.name_related,
                    "staff_id": employee.id,
                    "icon": "glyphicon glyphicon-user",
                    "class_id": time.id
                })
        index += 1
    patrol_area_list.append(patrol_area_dict)
"""
