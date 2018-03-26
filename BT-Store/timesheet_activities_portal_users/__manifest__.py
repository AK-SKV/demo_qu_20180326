# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2017 brain-tec AG (http://www.braintec-group.com)
# All Right Reserved
#
# See LICENSE file for full licensing details.
##############################################################################

{
    'name': "Timesheet activities for portal users",
    'summary': "Allows portal users to read / create / write / delete timesheet activities directly on the portal of Odoo",
    'description': """
Allows portal users to read / create / write / delete timesheet activities directly on the portal of Odoo
    """,
    'author': "brain-tec",
    'website': "http://www.braintec-group.com/",
    'category': 'Extra Tools',
    'version': '10.0.1.0.0',
    'price': 599,
    'currency': 'EUR',
    'license': 'OPL-1',
    'images': ['static/description/main_screenshot.png'],
    'external_dependencies': {
    },
    'depends': [
        'base',
        'web',
        'hr_timesheet',
        'website_portal',
    ],
    'data': [
        'views/account_analytic_line_templates.xml',
    ],
    'js': [],
}
