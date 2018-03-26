# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2017 brain-tec AG (http://www.braintec-group.com)
# All Right Reserved
#
# See LICENSE file for full licensing details.
##############################################################################

{
    'name': "Budget improved",
    'summary': "Extends the analytic accounts with new smart buttons.",
    'description': """
Extends the analytic accounts with new smart buttons.

- Button: "Sales" with the total amount of sales from all sales orders of an analytic account which are in state sale or done.

- Button "Invoice" with the total amount of the invoice lines of an analytic account whose invoices are in state open or paid.


Extends the calculation of budget lines:

- Calculating the Practical amount of the budget line when the analytic account is not set through account move lines.
    """,
    'author': "brain-tec",
    'website': "http://www.braintec-group.com/",
    'category': 'Extra Tools',
    'version': '10.0.1.0.0',
    'price': 9.99,
    'currency': 'EUR',
    'license': 'OPL-1',
    'images': ['static/description/main_screenshot.png'],
    'depends': [
        'base',
        'analytic',
        'account',
        'sale',
        'account_budget',
    ],
    'data': [
        'views/account_invoice_views.xml',
        'views/account_analytic_account_views.xml',
    ],
    'js': [],
}
