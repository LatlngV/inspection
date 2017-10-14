# -*- coding: utf-8 -*-

from odoo import api, fields, models


class RepairEmployee(models.TransientModel):
    _name = "inspection.repair_employee"
    _description = u"选择抢维修人员"

    def _get_repair_manager_id(self):
        return self.env["inspection.danger_manager"].browse(self._context.get("active_id"))

    danger_manager_id = fields.Many2one("inspection.danger_manager", string=u"抢维修人员", default=_get_repair_manager_id)
    repair_employee = fields.Many2many("hr.employee", "inspection_employee_repair", "repair_employee_id", "employee_id",
                                       string=u"抢维修人员", required=True)

    @api.multi
    def action_confirm(self):
        """
        更新维修管理表中的数据
        """
        if self.repair_employee:
            for record in self.repair_employee:
                self._cr.execute(
                    """UPDATE inspection_repair_manager SET repair_employee=%s, state='processing' WHERE danger=%s""" % (
                        record.id, self._context.get("active_id")))

            self.danger_manager_id.state = "agree"
            return True
