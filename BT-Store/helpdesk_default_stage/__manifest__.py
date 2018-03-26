# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2017 brain-tec AG (http://www.braintec-group.com)
# All Right Reserved
#
# See LICENSE file for full licensing details.
##############################################################################

{
    'name': "Helpdesk Default Stage",
    'summary': "Adds the functionality to define default helpdesk stages.",
    'description': """
After installing this module you can mark helpdesk stages as 'default'.\n
All default helpdesk stages will be added automatically to new helpdesk teams.
    """,
    'author': "brain-tec",
    'website': "http://www.braintec-group.com/",
    'category': 'Extra Tools',
    'version': '10.0.1.0.0',
    'price': 19.00,
    'currency': 'EUR',
    'license': 'OPL-1',
    'images': [
        'static/description/main_screenshot.png'
    ],
    'depends': [
        'base',
        'helpdesk',
    ],
    'data': [
        'views/helpdesk_stage_view_ext.xml',
    ],
    'js': [],
}
