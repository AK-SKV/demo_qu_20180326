# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2017 brain-tec AG (http://www.braintec-group.com)
# All Right Reserved
#
# See LICENSE file for full licensing details.
##############################################################################

{
    'name': "Leave management for portal users",
    'summary': "Allows portal users to manage their leaves directly on the portal of Odoo",
    'description': """
Allows portal users to manage their leaves directly on the portal of Odoo
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
        'hr_holidays',
        'website_portal',
        'website_enterprise',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_holidays_templates.xml',
    ],
    'js': [],
}
