# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from datetime import datetime
import hashlib
import requests
import time
import sys
from math import radians, cos, sin, asin, sqrt

reload(sys)
sys.setdefaultencoding("utf-8")


class GPSManager(models.Model):
    _name = "inspection.gps_manager"
    _description = u"GPS 设备管理"

    name = fields.Char(string=u"设备名称", required=True)
    staff = fields.Many2one("hr.employee", string=u"绑定人员", domain=[("select_job", "=", "patrol_employee")])
    number = fields.Char(string=u"设备号码")
    imei = fields.Char(string=u"设备号(IMEI)", required=True)
    phone = fields.Char(string=u"设备电话号码")
    latitude = fields.Float(string=u"纬度坐标", digits=(9, 6))
    longitude = fields.Float(string=u"经度坐标", digits=(9, 6))
    speed = fields.Float(string=u"速度", digits=(5, 2))
    gps_time = fields.Char(string=u"定位时间")
    power = fields.Char(string=u"电量")
    device_info = fields.Integer(string=u"设备信息")
    device_info_new = fields.Integer(string=u"新设备信息")

    _sql_constraints = [
        (u"唯一的设备号",
         "UNIQUE(imei)",
         u"设备号已存在，请检查设备号(IMEI)"),

        (u"唯一用户",
         "UNIQUE(staff)",
         u"该巡线员已绑定设备，请重新选择巡线员"),
    ]


class SystemUser(models.Model):
    _name = "inspection.system_user"
    _description = u"登陆汽车在线后台的用户"
    _rec_name = "username"

    username = fields.Char(string=u"登陆账号", required=True)
    password = fields.Char(string=u"用户密码", required=True)
    access_token = fields.Char(string=u"Access Token", readonly=True)
    is_bind = fields.Boolean(string=u"是否绑定", default=False)
    begin_time = fields.Char(string=u"开始时间", default=0)
    data_position = fields.Char(string=u"最后一条数据的 id", default=0)

    @api.multi
    def action_access_token(self):
        """
        获取 Access Token: (本来可以直接获取用户和密码，但为了定时任务不能直接获取)
            1. 根据用户名和密码还有加密方式获取 Access Token
            2. 写入到数据库表中
        """
        system_users = self.env["inspection.system_user"].search([])
        for system_user in system_users:
            username = system_user.username
            password = system_user.password
            if username and password:
                # 根据 API 接口获取 access_token
                time_stamp = int(time.time())
                m1 = hashlib.md5()
                m1.update(password)
                md5_pd = m1.hexdigest()
                m2 = hashlib.md5()
                m2.update(md5_pd + str(time_stamp))
                signature = m2.hexdigest()
                url = "http://api.gpsoo.net/1/auth/access_token"
                params = {"account": username, "time": time_stamp, "signature": signature}
                return_json = requests.get(url=url, params=params).json()
                if return_json["ret"] == 0:
                    if not system_user.is_bind:
                        self._cr.execute(
                            """CREATE TABLE DOTOP_STAFF_POSITION(id bigserial PRIMARY KEY, staff_id INT, latitude FLOAT, longitude FLOAT, imei VARCHAR, speed FLOAT, gps_time BIGINT)""")
                        self._cr.execute(
                            """CREATE TABLE staff_task (id bigserial PRIMARY KEY, staff_id INT, point_count INT, create_time BIGINT)""")
                        self._cr.execute(
                            """CREATE TABLE staff_task_detail(id bigserial PRIMARY KEY, task_id BIGINT, staff_id INT, default_range boolean, one_hundred_range boolean, two_hundred_range boolean, five_hundred_range boolean, thousand_range boolean, point_id INT, create_time BIGINT)""")
                    self.write({"access_token": return_json["access_token"], "is_bind": True, "begin_time": time_stamp})
                else:
                    raise ValidationError(return_json["msg"])

    @api.multi
    def action_update_gps(self):
        """
        更新 GPS 设备
            1. 获取 Access Token 请求 json 数据
            2. 写入到数据库表中
        """
        if self.access_token:
            gps_manager = self.env["inspection.gps_manager"]
            url = "http://api.gpsoo.net/1/account/devinfo"
            params = {"access_token": self.access_token, "target": self.username}
            return_json = requests.get(url=url, params=params).json()
            if return_json["ret"] == 0:
                for data in return_json["data"]:
                    imei = data["imei"]
                    name = data["name"]
                    search_imei = self.env["inspection.gps_manager"].search([("imei", "=", imei)])
                    if len(search_imei) > 0:
                        gps_manager.write({"name": name, "imei": imei})
                    else:
                        continue
            else:
                raise ValidationError(return_json["msg"])
        else:
            raise ValidationError(u"请先获取 Access Token")

    def get_monitor(self):
        """
        实时监控:
            1. 获取账号和 Access Token
            2. 请求 json 数据
            3. 更新数据库表里的数据
        """
        system_users = self.env["inspection.system_user"].search([])
        for system_user in system_users:
            user_name = system_user.username
            access_token = system_user.access_token
            time_stamp = int(time.time())
            if system_user.username and system_user.access_token:
                url = "http://api.gpsoo.net/1/account/monitor"
                params = {"access_token": access_token, "target": user_name, "time": time_stamp, "map_type": "GOOGLE"}
                return_json = requests.get(url=url, params=params).json()
                if return_json["ret"] == 0 and return_json["msg"] == "OK":
                    for data in return_json["data"]:
                        imei = data["imei"]
                        gps_time = data["gps_time"]
                        latitude = data["lat"]
                        longitude = data["lng"]
                        speed = data["speed"]
                        if "power" not in data:
                            power = "未知电量"
                        else:
                            power = data["power"]
                        device_info = data["device_info"]
                        device_info_new = data["device_info_new"]
                        gps_managers = self.env["inspection.gps_manager"].search([("imei", "=", imei)])
                        for gps_manager in gps_managers:
                            if gps_manager.staff:
                                gps_manager.write({"latitude": latitude, "longitude": longitude, "speed": speed,
                                                   "gps_time": gps_time, "power": power, "device_info": device_info,
                                                   "device_info_new": device_info_new})
                else:
                    raise ValidationError(return_json["msg"])

    def get_history(self):
        """
        历史轨迹
            1. 获取 Access Token
            2. 请求 json 数据
            3. 根据 IMEI 写入数据
        """
        current_time = int(time.time())
        data_position = 0
        system_users = self.env["inspection.system_user"].search([])
        for system_user in system_users:
            if system_user.access_token:
                # 更新表里数据的最新位置
                self._cr.execute("""SELECT id FROM DOTOP_STAFF_POSITION ORDER BY id DESC limit 1""")
                for position in self._cr.fetchall():
                    if position[0] != 0 and position[0] is not None:
                        system_user.write({"data_position": position[0]})
                        data_position = position[0]
                gps_managers = self.env["inspection.gps_manager"].search([])
                for gps_manager in gps_managers:
                    if gps_manager.staff:
                        url = "http://api.gpsoo.net/1/devices/history"
                        params = {"access_token": system_user.access_token, "imei": gps_manager.imei,
                                  "map_type": "GOOGLE", "begin_time": system_user.begin_time, "end_time": current_time,
                                  "time": current_time}
                        return_json = requests.get(url=url, params=params).json()
                        print return_json
                        if return_json["ret"] == 0 and return_json["msg"] == "OK":
                            if len(return_json["data"]) > 0:
                                for data in return_json["data"]:
                                    latitude = data["lat"]
                                    longitude = data["lng"]
                                    speed = data["speed"]
                                    gps_time = data["gps_time"]
                                    self._cr.execute(
                                        """INSERT INTO DOTOP_STAFF_POSITION (staff_id, latitude, longitude, imei, speed, gps_time) VALUES ('%s', '%s', '%s', '%s', '%s', '%s')""" % (
                                            gps_manager.staff.id, latitude, longitude, gps_manager.imei, speed,
                                            int(gps_time)))
                        else:
                            raise ValidationError(return_json["msg"])
                # 更新开始查询的时间
                system_user.write({"begin_time": current_time})
            else:
                raise ValidationError(u"请先获取 Access Token")
        # 同步数据
        self._synchronize_data(data_position)

    def _synchronize_data(self, data_position):
        """
        同步数据
        """
        table_name = self._table_name()
        # 表不存在就创建表
        self._cr.execute(
            """CREATE TABLE if not exists %s (id bigserial PRIMARY KEY, staff_id INT, latitude FLOAT, longitude FLOAT, imei VARCHAR, speed FLOAT, gps_time BIGINT)""" % table_name)
        # 查询用户自定义的数据库表
        # self._cr.execute("""SELECT tablename FROM pg_tables WHERE schemaname='public' AND tablename LIKE 'dotop%'""")

        # 记录含有当前表的标志位
        # have_index = 0
        # 记录没有当前表的标志位
        # no_index = 0
        # for r in self._cr.fetchall():
        #     if table_name != r[0]:
        #         have_index += 1
        #     no_index += 1

        # 如果表不存在就创建表
        # if have_index == no_index:
        #     self._cr.execute(
        #         """CREATE TABLE %s(id bigserial PRIMARY KEY, staff_id INT, latitude FLOAT, longitude FLOAT, imei VARCHAR, speed FLOAT, gps_time BIGINT)""" % table_name)
        #     self._cr.execute("""DELETE FROM DOTOP_STAFF_POSITION WHERE id<%s""" % data_position)
        # 插入数据
        self._cr.execute("""SELECT * FROM DOTOP_STAFF_POSITION WHERE id>=%s""" % data_position)
        for row in self._cr.fetchall():
            if len(row) > 0:
                self._cr.execute(
                    """INSERT INTO %s (staff_id, latitude, longitude, imei, speed, gps_time) VALUES (%s, %s, %s, %s, %s, %s)""" % (
                        table_name, row[1], row[2], row[3], row[4], row[5], row[6]))

    @staticmethod
    def _table_name():
        """
        获取表名
        :return: 表名
        """
        current_datetime = datetime.now()
        current_year = str(current_datetime.year)
        current_month = str(current_datetime.month)
        if len(current_month) == 1:
            current_month = "0" + current_month
        table_name = "dotop_" + current_year + current_month
        return table_name

    @api.multi
    def _staff_task(self):
        """
        生成员工任务
        """
        # 根据巡线员生成任务
        staffs = self.env["hr.employee"].search([("select_job", "=", "patrol_employee")])
        attendance_times = self.env["inspection.attendance_time"].search([])
        for staff in staffs:
            for attendance_time in attendance_times:
                # 获取巡线员必经点个数
                staff_points = self.env["inspection.staff_point"].search([("belong_staff.id", "=", staff.id)])
                point_count = len(staff_points)

                # 创建时间：强行设置为巡线员考勤的开始时间
                start_time_list = str(attendance_time.start_time).split(".")
                minutes = start_time_list[1]
                if minutes != 0:
                    minutes = str(int(float(minutes) * 3 / 5))
                if len(minutes) == 1:
                    minutes = "0" + minutes
                date = time.strftime("%Y-%m-%d", time.localtime(time.time())) + " " + start_time_list[
                    0] + ":" + minutes + ":00"
                time_array = time.strptime(date, "%Y-%m-%d %H:%M:%S")
                date_time_stamp = int(time.mktime(time_array)) - 8 * 60 * 60
                self._cr.execute(
                    """INSERT INTO staff_task (staff_id, point_count, create_time) VALUES (%s, %s, %s)""" % (
                        staff.id, point_count, date_time_stamp))

    def _staff_task_detail(self):
        """
        员工任务详情，今天的任务详情是昨天的完成情况
        """
        attendance_times = self.env["inspection.attendance_time"].search([])
        for attendance_time in attendance_times:
            start_time_stamp = self._time_stamp(attendance_time.start_time)
            end_time_stamp = self._time_stamp(attendance_time.end_time)
            print start_time_stamp, end_time_stamp
            self._cr.execute("""SELECT id, staff_id FROM staff_task WHERE create_time=%s""" % start_time_stamp)
            for row in self._cr.fetchall():
                staff_points = self.env["inspection.staff_point"].search([("belong_staff.id", "=", row[1])])
                for staff_point in staff_points:
                    default_range_flag = False
                    one_hundred_range_flag = False
                    two_hundred_range_flag = False
                    five_hundred_range_flag = False
                    thousand_range_flag = False

                    staff_point_latitude = staff_point.latitude
                    staff_point_longitude = staff_point.longitude

                    self._cr.execute(
                        """SELECT latitude,longitude FROM dotop_staff_position WHERE staff_id=%s AND gps_time>=%s AND gps_time<=%s""" % (
                            row[1], start_time_stamp, end_time_stamp))
                    for record in self._cr.fetchall():
                        """
                        计算坐标点在必经点范围内
                        """
                        staff_history_latitude = record[0]
                        staff_history_longitude = record[1]

                        distance = self._haversine(staff_point_longitude, staff_point_latitude, staff_history_longitude,
                                                   staff_history_latitude)
                        if float(50) >= distance > 0:
                            default_range_flag = True
                            one_hundred_range_flag = True
                            two_hundred_range_flag = True
                            five_hundred_range_flag = True
                            thousand_range_flag = True
                            break
                        elif float(100) >= distance > float(50):
                            one_hundred_range_flag = True
                            two_hundred_range_flag = True
                            five_hundred_range_flag = True
                            thousand_range_flag = True
                            break
                        elif float(200) >= distance > float(100):
                            two_hundred_range_flag = True
                            five_hundred_range_flag = True
                            thousand_range_flag = True
                            break
                        elif float(500) >= distance > float(200):
                            five_hundred_range_flag = True
                            thousand_range_flag = True
                            break
                        elif float(1000) >= thousand_range_flag > 500:
                            thousand_range_flag = True
                            break
                    self._cr.execute(
                        """INSERT INTO staff_task_detail (task_id, staff_id, default_range, one_hundred_range, two_hundred_range, five_hundred_range, thousand_range, point_id, create_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                        (row[0], staff_point.belong_staff.id, default_range_flag, one_hundred_range_flag,
                         two_hundred_range_flag, five_hundred_range_flag, thousand_range_flag, staff_point.id,
                         int(time.time()) - 24 * 60 * 60))

    def _time_stamp(self, float_time):
        """
        拼接时间字符串并转化成时间戳
        :param float_time: float 类型时间（时分）
        :return: 时间戳
        """
        time_list = str(float_time).split(".")
        minutes = time_list[1]
        if minutes != 0:
            if len(minutes) == 1:
                minutes = "0" + minutes
            minutes = str(int(float(minutes) * 3 / 5))
        date = time.strftime("%Y-%m-%d", time.localtime(time.time())) + " " + time_list[0] + ":" + minutes + ":00"
        time_array = time.strptime(date, "%Y-%m-%d %H:%M:%S")
        time_stamp = int(time.mktime(time_array)) - 32 * 60 * 60
        return time_stamp

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
        return c * r * 1000

    @api.multi
    def _delete_history_from_staff_position(self):
        """
        从巡线轨迹表中删除数据
        """
        # 获取当前时间
        date = time.strftime("%Y-%m-%d", time.localtime(time.time())) + " 00:00:00"
        time_array = time.strptime(date, "%Y-%m-%d %H:%M:%S")
        time_stamp = int(time.mktime(time_array)) - 10 * 24 * 60 * 60
        print time_stamp

        delete = """DELETE FROM DOTOP_STAFF_POSITION WHERE gps_time<=%s""" % time_stamp
        self._cr.execute(delete)
