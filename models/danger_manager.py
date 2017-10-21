# -*- coding: utf-8 -*-

from odoo import api, fields, models
import requests
import time


class DangerManager(models.Model):
    _name = "inspection.danger_manager"
    _description = u"隐患管理"
    _rec_name = "danger_type"

    STATE_PROCESS = [("untreated", u"未处理"), ("agree", u"已同意维修"), ("refuse", u"未同意维修")]

    patrol_area = fields.Many2one("hr.department", string=u"巡线管理区", readonly=True)
    patrol_section = fields.Many2one("inspection.patrol_section", string=u"巡线段", readonly=True)
    danger_type = fields.Many2one("inspection.danger_category", string=u"隐患类别", readonly=True)
    danger_level = fields.Many2one("inspection.danger_level", string=u"隐患级别", readonly=True)
    find_staff = fields.Many2one("hr.employee", string=u"发现人", readonly=True)
    report_time = fields.Datetime(string=u"上报时间", readonly=True)
    latitude = fields.Float(string=u"纬度坐标", digits=(9, 6), readonly=True)
    longitude = fields.Float(string=u"经度坐标", digits=(9, 6), readonly=True)
    address = fields.Text(string=u"地理位置", readonly=True)
    state = fields.Selection(STATE_PROCESS, string=u"处理状态", default="untreated")
    detail = fields.Text(string=u"隐患详情", readonly=True)

    @api.multi
    def action_agree(self):
        """
        同意
        """
        repair_manager = self.env["inspection.repair_manager"]
        repair_manager.create({
            "category": self.danger_type.id,
            "level": self.danger_level.id,
            "find_employee": self.find_staff.id,
            "upload_time": self.report_time,
            "danger": self.id,
            "latitude": self.latitude,
            "longitude": self.longitude
        })
        return {
            "name": u"选择抢维修人员",
            "type": "ir.actions.act_window",
            "src_model": "inspection.danger_manager",
            "res_model": "inspection.repair_employee",
            "view_mode": "form",
            "target": "new",
        }

    @api.multi
    def action_refuse(self):
        """
        拒绝
        """
        self.state = "refuse"
        return True


class ReportDanger(models.Model):
    _name = "inspection.report_danger"
    _description = u"隐患上报"
    _rec_name = "danger_type"

    def _get_employee(self):
        """
        根据当前登录用户获取员工
        """
        user_id = self.env.user.id
        employees = self.env["hr.employee"].search([])
        for employee in employees:
            if employee.resource_id.user_id.id == user_id:
                return employee.id

    staff = fields.Many2one("hr.employee", string=u"巡线员", default=_get_employee)
    danger_type = fields.Many2one("inspection.danger_category", string=u"隐患类别", required=True)
    danger_level = fields.Many2one("inspection.danger_level", string=u"隐患级别", required=True)
    create_time = fields.Datetime(string=u"上报时间", default=fields.Datetime.now())
    latitude = fields.Float(string=u"纬度坐标", digits=(9, 6), readonly=True)
    longitude = fields.Float(string=u"经度坐标", digits=(9, 6), readonly=True)
    detail = fields.Text(string=u"隐患详情", required=True)
    readonly = fields.Boolean(string=u"是否只读", default=False)

    @api.model
    def create(self, values):
        """
        重写 create 方法
        """
        values["readonly"] = True
        # 插入数据
        employee_id = self._get_employee()
        # 获取员工部门
        employees = self.env["hr.employee"].search([("id", "=", employee_id)])
        for employee in employees:
            department_id = employee.id
        # 获取员工巡线段
        patrol_sections = self.env["inspection.patrol_section"].search([("patrol_employee", "=", employee_id)])
        for patrol_section in patrol_sections:
            section_id = patrol_section.id
        # 获取员工经纬度坐标以及地理位置
        system_users = self.env["inspection.system_user"].search([])
        time_stamp = int(time.time())
        for system_user in system_users:
            if system_user.access_token:
                # 请求经纬度坐标
                url = "http://api.gpsoo.net/1/account/monitor"
                params = {"access_token": system_user.access_token, "target": system_user.username, "time": time_stamp,
                          "map_type": "GOOGLE"}
                return_json = requests.get(url=url, params=params).json()
                if return_json["ret"] == 0 and return_json["msg"] == "OK":
                    gps_managers = self.env["inspection.gps_manager"].search([("staff.id", "=", employee_id)])
                    for gps_manager in gps_managers:
                        if gps_manager.imei:
                            imei = gps_manager.imei
                            for data in return_json["data"]:
                                if data["imei"] == imei:
                                    latitude = data["lat"]
                                    longitude = data["lng"]
                                    self.write({"latitude": latitude, "longitude": longitude})
                                    # 逆地理位置解析
                                    address_url = "http://api.gpsoo.net/1/tool/address"
                                    address_params = {"access_token": system_user.access_token, "lng": longitude,
                                                      "account": system_user.username, "lat": latitude,
                                                      "time": time_stamp, "map_type": "GOOGLE"}
                                    address_json = requests.get(url=address_url, params=address_params).json()
                                    if address_json["ret"] == 0 and address_json["msg"] == "":
                                        address = address_json["address"]
                                        # 在隐患管理表中插入数据
                                        self.env["inspection.danger_manager"].create({
                                            "danger_type": values.get("danger_type"),
                                            "danger_level": values.get("danger_level"),
                                            "find_staff": employee_id,
                                            "report_time": fields.Datetime.now(),
                                            "detail": values.get("detail"),
                                            "patrol_area": department_id,
                                            "patrol_section": section_id,
                                            "latitude": latitude,
                                            "longitude": longitude,
                                            "address": address})
                                    else:
                                        raise RuntimeError(address_json["msg"])
                else:
                    raise RuntimeError(return_json["msg"])
        return super(ReportDanger, self).create(values)


class RepairManager(models.Model):
    _name = "inspection.repair_manager"
    _description = u"维修管理"
    _rec_name = "category"

    SELECT_RESULT = [("unassigned", u"未指派"), ("processing", u"处理中"), ("complete", u"已完成")]

    category = fields.Many2one("inspection.danger_category", string=u"事故类别", readonly=True)
    danger = fields.Many2one("inspection.danger_manager", string=u"隐患管理")
    level = fields.Many2one("inspection.danger_level", string=u"事故级别", readonly=True)
    find_employee = fields.Many2one("hr.employee", string=u"发现人", readonly=True)
    repair_employee = fields.Many2one("hr.employee", string=u"抢维修人员", readonly=True)
    state = fields.Selection(SELECT_RESULT, string=u"结果", default="unassigned")
    upload_time = fields.Datetime(string=u"上报时间", readonly=True)
    latitude = fields.Float(string=u"纬度坐标", digits=(9, 6), readonly=True)
    longitude = fields.Float(string=u"经度坐标", digits=(9, 6), readonly=True)

    @api.multi
    def action_process(self):
        self.state = "complete"
        return True

    @api.multi
    def action_repair_map(self):
        """
        向导
        """
        return {
            "name": u"维修地图",
            "type": "ir.actions.act_window",
            "src_model": "inspection.repair_manager",
            "res_model": "inspection.repair_map",
            "view_mode": "form",
            "target": "new",
        }


class DangerCategory(models.Model):
    _name = "inspection.danger_category"
    _description = u"隐患类别"

    name = fields.Char(string=u"隐患类别名称", required=True)
    image = fields.Binary(string=u"地图图标", attachment=True, required=True)
    remark = fields.Text(string=u"备注", required=True)


class DangerLevel(models.Model):
    _name = "inspection.danger_level"
    _description = u"隐患级别"

    name = fields.Char(string=u"隐患级别名称", required=True)
    remark = fields.Text(string=u"备注", required=True)
