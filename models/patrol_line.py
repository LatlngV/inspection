# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError
import threading
import sys
import os

reload(sys)
sys.setdefaultencoding("utf-8")


class PatrolSection(models.Model):
    _name = "inspection.patrol_section"
    _description = u"巡线段"
    _rec_name = "area_name"

    belong_area = fields.Many2one("hr.department", string=u"所属区域", required=True)
    area_name = fields.Char(string=u"区段名称", required=True)
    affiliated_lines = fields.Char(string=u"所属线路", default=u"未知线路")
    patrol_employee = fields.Many2one("hr.employee", string=u"巡线人员", domain=[("select_job", "=", "patrol_employee")])
    pipeline_length = fields.Float(string=u"管线长度(km)", required=True, digits=(10, 2))
    file_name = fields.Char(string=u"文件名称")
    file = fields.Binary(string=u"上传KML文件", attachment=True, required=True)
    remark = fields.Text(string=u"备注")
    create_date = fields.Datetime(string=u"创建时间", default=fields.Datetime.now(), readonly=True)
    stream = fields.Integer(string=u"文件流", compute="_get_latlng")
    is_parse = fields.Boolean(string=u"是否解析", default=False)

    _sql_constraints = [
        (u"文件名唯一",
         "UNIQUE(file_name)",
         u"该文件已存在!")
    ]

    @api.constrains("file_name")
    def _constraint_file_name(self):
        for record in self:
            name = record.file_name
            if name[-4:] != ".kml":
                raise ValidationError(u"上传的不是 KML 文件！")

    @api.onchange("file_name")
    def _get_latlng(self):
        """
            上传 KML 文件，获取当前界面的 id，根据 id 生成点的记录
        """
        self._cr.execute("""SELECT * FROM ir_attachment WHERE res_model = 'inspection.patrol_section'""")

        # 管线的点
        patrol_point = self.env["inspection.patrol_point"]

        """
            1. 解析 KML 文件
            2. 将 KML 文件中的数据写入到数据库中
        """
        for row in self._cr.dictfetchall():
            if not self.is_parse:
                if self.area_name == row["res_name"]:
                    db_name = threading.current_thread().dbname
                    file_path = "data/filestore/" + db_name + "/" + row["store_fname"]
                    file = open(file_path, "rb")
                    try:
                        # 整行整行的读取文本内容，将文本内容拼接成一行
                        file_list = file.readlines()
                        content = ""
                        for line in file_list:
                            content += line.strip()

                        # 根据唯一标识拆分文本内容，获得点的 list
                        line_string = content.split("<LineString>")[1]
                        coordinates = line_string.split("<coordinates>")[1]
                        points = coordinates.split("</coordinates>")[0]
                        point_list = points.split(" ")

                        # 遍历点的 list， 将一组一组的点拆分，写入到 inspection.patrol_section 表中
                        for point in point_list:
                            latlng = point.split(",")
                            longitude = latlng[0]
                            latitude = latlng[1]
                            patrol_point.create({"point_name": u"未命名坐标", "belong_section": self.id,
                                                 "attendance_range": 50, "latitude": latitude, "longitude": longitude})

                        # 将标志位设置为 True
                        self.write({"is_parse": True})
                    finally:
                        file.close()

    @api.multi
    def write(self, values):
        """
        重写 write 方法
        :param values: 变更的字段，以字典的形式体现
        """
        super(PatrolSection, self).write(values)

    @api.multi
    def unlink(self):
        """
        重写删除方法
        """
        self._cr.execute(
            """SELECT res_name, store_fname FROM ir_attachment WHERE res_model = 'inspection.patrol_section'""")
        for row in self._cr.fetchall():
            for record in self:
                if record.area_name == row[0]:
                    db_name = threading.current_thread().dbname
                    path = "data/filestore/" + db_name + "/" + row[1]
                    if os.path.exists(path):
                        os.remove(path)
                        patrol_points = self.env["inspection.patrol_point"].search(
                            [("belong_section.area_name", "=", row[0])])
                        for patrol_point in patrol_points:
                            patrol_point.unlink()
        return super(PatrolSection, self).unlink()


class PatrolPoint(models.Model):
    _name = "inspection.patrol_point"
    _description = u"管线点"
    _rec_name = "point_name"

    point_name = fields.Char(string=u"管线点名字", default=u"未命名地标", required=True)
    belong_area = fields.Many2one("hr.department", string=u"所属区域", compute="_compute_area", store=True)
    belong_section = fields.Many2one("inspection.patrol_section", string=u"所属区段", required=True)
    latitude = fields.Float(string=u"纬度坐标", digits=(13, 10), required=True)
    longitude = fields.Float(string=u"经度坐标", digits=(13, 10), required=True)
    create_date = fields.Datetime(string=u"创建时间", default=fields.Datetime.now(), readonly=True)

    _sql_constraints = [
        (u"有效的考勤范围",
         "CHECK(attendance_range >= 0)",
         u"考勤范围必须是大于等于 0 的正整数"),
    ]

    @api.depends("belong_section")
    def _compute_area(self):
        """
        所属区域
        """
        for record in self:
            record.belong_area = record.belong_section.belong_area


class StaffPointKML(models.Model):
    _name = "inspection.staff_point_kml"
    _description = u"巡线员必经点的 kml"
    _rec_name = "staff_name"

    staff_name = fields.Many2one("hr.employee", string=u"巡线员", required=True)
    file_name = fields.Char(string=u"文件名称")
    file = fields.Binary(string=u"上传KML文件", attachment=True, required=True)
    stream = fields.Integer(string=u"文件流", compute="_read_file")
    is_parse = fields.Boolean(string=u"是否解析", default=False)
    create_date = fields.Datetime(string=u"创建时间", default=fields.Datetime.now(), readonly=True)

    _sql_constraints = [
        (u"文件名唯一",
         "UNIQUE(file_name)",
         u"该文件已存在!")
    ]

    @api.constrains("file_name")
    def _constraint_file_name(self):
        for record in self:
            name = record.file_name
            if name[-4:] != ".kml":
                raise ValidationError(u"上传的不是 KML 文件！")

    @api.depends("file_name")
    def _read_file(self):
        """
        把巡线员必经点写入到数据库
        """
        self._cr.execute(
            """SELECT res_name, store_fname FROM ir_attachment WHERE res_model = 'inspection.staff_point_kml'""")
        for row in self._cr.fetchall():
            if not self.is_parse:
                if len(row[0]) != 0 and row[0] == self.staff_name.name_related:
                    db_name = threading.current_thread().dbname
                    path = "data/filestore/" + db_name + "/" + row[1]
                    file_list = open(path, "r").readlines()
                    content = ""
                    for line in file_list:
                        content += line.strip()

                    staff_point = self.env["inspection.staff_point"]
                    content_list = content.split("<Placemark>")
                    for text in content_list:
                        if "<Point>" in text:
                            """
                            拆分巡线员必经点的坐标
                            """
                            text_list = text.split("<coordinates>")
                            point = text_list[1].split("</coordinates>")
                            point_list = point[0].split(",")

                            """
                            获取必经点的名字
                            """
                            name_list = text_list[0].split("<name>")
                            name = name_list[1].split("</name>")
                            staff_point.create(
                                {"staff_point_name": name[0], "latitude": point_list[1], "longitude": point_list[0],
                                 "create_date": fields.Datetime.now(), "belong_staff": self.staff_name.id,
                                 "belong_area": self.staff_name.department_id.id})
                    self.write({"is_parse": True})

    @api.multi
    def write(self, values):
        """
        重写 write 方法
        :param values: 变更的字段，以字典的形式体现
        """
        return super(StaffPointKML, self).write(values)

    @api.multi
    def unlink(self):
        """
        重写删除方法
        """
        self._cr.execute(
            """SELECT res_name, store_fname FROM ir_attachment WHERE res_model = 'inspection.staff_point_kml'""")
        for row in self._cr.fetchall():
            for record in self:
                if record.staff_name.name_related == row[0]:
                    db_name = threading.current_thread().dbname
                    path = "data/filestore/" + db_name + "/" + row[1]
                    if os.path.exists(path):
                        os.remove(path)
                        staff_points = self.env["inspection.staff_point"].search(
                            [("belong_staff.name_related", "=", row[0])])
                        print staff_points
                        for staff_point in staff_points:
                            staff_point.unlink()
        return super(StaffPointKML, self).unlink()


class PatrolStaffPoint(models.Model):
    _name = "inspection.staff_point"
    _description = u"巡线员必经点"
    _rec_name = "staff_point_name"

    staff_point_name = fields.Char(string=u"必经点名字", default=u"未命名地标", required=True)
    belong_area = fields.Many2one("hr.department", string=u"所属区域", compute="_compute_area", store=True)
    belong_staff = fields.Many2one("hr.employee", string=u"巡线员")
    latitude = fields.Float(string=u"纬度坐标", digits=(13, 10), required=True)
    longitude = fields.Float(string=u"经度坐标", digits=(13, 10), required=True)
    create_date = fields.Datetime(string=u"创建时间", default=fields.Datetime.now(), readonly=True)
    attendance_range = fields.Integer(string=u"考勤范围(米)", default=50, required=True)

    _sql_constraints = [
        (u"有效的考勤范围",
         "CHECK(attendance_range >= 0)",
         u"考勤范围必须是大于等于 0 的正整数"),
    ]


class AttendanceTime(models.Model):
    _name = "inspection.attendance_time"
    _description = u"考勤时间"

    name = fields.Char(string=u"考勤名称", required=True)
    start_time = fields.Float(string=u"开始时间", required=True)
    end_time = fields.Float(string=u"结束时间", required=True)
    remark = fields.Text(string=u"备注")
    employee_id = fields.Many2many("hr.employee", "inspection_time_employee", "time_id", "employee_id", string=u"考勤人员",
                                   domain=[("select_job", "=", "patrol_employee")])


class AttendanceEmployee(models.Model):
    _name = "inspection.attendance_employee"
    _description = u"考勤人员"
    _rec_name = "employee"

    time_id = fields.Many2one("inspection.attendance_time", string=u"考勤名称")
    employee = fields.Many2one("hr.employee", string=u"员工", required=True)
