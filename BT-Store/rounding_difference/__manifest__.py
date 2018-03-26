# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2017 brain-tec AG (http://www.braintec-group.com)
# All Right Reserved
#
# See LICENSE file for full licensing details.
##############################################################################
{
    'name': "Rounding difference",
    'summary': "Compute rounding differences on invoices",
    'description': "This module allows you to automatically compute rounding differences on invoices.",
    'author': "brain-tec",
    'website': "http://www.braintec-group.com",
    'category': 'Accounting',
    'version': '1.0',
    'price': 9.99,
    'currency': 'EUR',
    'license': 'OPL-1',
    'images': ['static/description/screenshot.png'],
    'depends': ['base',
                'account'],
    "data": ['data/account_account.xml',
             'data/product_product.xml',
             'views/res_company_ext.xml'],
}