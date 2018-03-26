# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2017 brain-tec AG (http://www.braintec-group.com)
# All Right Reserved
#
# See LICENSE file for full licensing details.
##############################################################################

{
    'name': "Stop Schedulers",
    'summary': "Allows to easily inhibit all the schedulers at once.",
    'description': "Allows to inhibit all the schedulers at once, and to "
                   "enable them later, without having to remember which ones "
                   "were active, therefore providing a convenient way to stop "
                   "the automated tasks of Odoo when needed, and to easily "
                   "restore the past behaviour.",
    'author': "brain-tec",
    'website': "http://www.braintec-group.com",
    'category': 'Extra Tools',
    'version': '10.0.1.0.0',
    'price': 9.95,
    'currency': 'EUR',
    'license': 'OPL-1',
    'images': [
        'static/description/main_screenshot.png',
    ],
    'depends': [
        'base',
        'base_setup',
    ],
    'data': [
        'views/res_config_view.xml',
    ],
}
