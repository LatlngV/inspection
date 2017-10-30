# -*- coding: utf-8 -*-

{
    "name": "巡检系统",
    "summary": "企业专用巡检系统",
    "author": "Latlng",
    "sequence": "0",
    "version": "1.0",
    "depends": ["hr"],
    "website": "http://www.eyesw.cn",
    "data": [
        "security/inspection_security.xml",
        "security/ir.model.access.csv",
        "views/hr_views.xml",
        "views/attendance_views.xml",
        "views/danger_manager_views.xml",
        "views/patrol_views.xml",
        "views/web_templates.xml",
        "views/google_map_views.xml",
        "views/system_user_views.xml",
        "views/patrol_track_template.xml",
        "views/staff_report_template.xml",
        "views/repair_map_template.xml",
        "views/staff_task_detail_template.xml",
        "views/attendance_time_template.xml",
        "views/gps_manager_views.xml",
        "data/timing_task_views.xml",
        "views/menu_item.xml",
        "wizard/repair_employee_views.xml",
        "wizard/repair_map_views.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
    "description": """
这是一套企业级的巡线系统
=======================
里面包含许多隐私信息，使用者注意信息泄露问题

违反者将追究法律责任
    """,
}
