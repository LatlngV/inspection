# -*- coding: utf-8 -*-

from odoo import fields, models
import sys

reload(sys)
sys.setdefaultencoding("utf8")


class Employee(models.Model):
    _inherit = "hr.employee"
    _description = u"员工"

    SELECT_JOB = [("patrol_employee", u"巡线人员"), ("no_patrol_employee", u"非巡线人员")]

    job_number = fields.Char(string=u"工号", required=True)
    device_number = fields.Char(string=u"设备串号", required=True)
    wei_chat = fields.Char(string=u"微信号")
    create_date = fields.Datetime(string=u"创建时间", default=fields.Datetime.now(), readonly=True)
    select_job = fields.Selection(SELECT_JOB, string=u"巡线人员", default="patrol_employee")

    _sql_constraints = [
        (u"唯一工号",
         "UNIQUE(job_number)",
         u"工号必须是唯一的，不能重复！"),

        (u"唯一设备串号",
         "UNIQUE(device_number)",
         u"设备串号必须是唯一的，不能重复！"),
    ]


class Department(models.Model):
    _inherit = "hr.department"
    _description = u"部门"

    patrol_department = fields.Boolean(string=u"巡线部门", default=False)
