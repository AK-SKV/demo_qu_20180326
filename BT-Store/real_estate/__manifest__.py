# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2017 brain-tec AG (http://www.braintec-group.com)
# All Right Reserved
#
# See LICENSE file for full licensing details.
##############################################################################
{
    'name': "Real Estate",
    'summary': "Manage your Real Estate",
    'description': "Manage your Real Estate",
    'author': "brain-tec",
    'website': "http://www.braintec-group.com",
    'category': 'Extra Tools',
    'version': '1.0',
    'price': 99.00,
    'currency': 'EUR',
    'license': 'OPL-1',
    'images': ['static/description/main_screenshot.png'],
    'depends': ['base',
                'account',
                'sale',
                'purchase',
                'sale_contract'],
    "data": ['security/security.xml',
             'security/ir.model.access.csv',
             'views/menu.xml',
             'views/account_invoice_ext.xml',
             'views/building.xml',
             'views/building_category.xml',
             'views/purchase_order_ext.xml',
             'views/res_partner_ext.xml',
             'views/sale_order_ext.xml',
             'views/sale_subscription_ext.xml'],
}