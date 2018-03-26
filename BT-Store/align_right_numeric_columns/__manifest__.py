# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2017 brain-tec AG (http://www.braintec-group.com)
# All Right Reserved
#
# See LICENSE file for full licensing details.
##############################################################################

{
    'name': "Tree view IMP: Align right numeric columns",
    'summary': "In tree views, numeric values are aligned at right while labels are aligned at left: This module align numeric columns with their values",
    'description': """
- Numeric values are aligned at right in the tree views.
- Labels are aligned at left.

This module align numeric columns with their values: at right

    """,
    'author': "brain-tec",
    'website': "http://www.braintec-group.com/",
    'category': 'Extra Tools',
    'version': '10.0.1.0.0',
    'price': 4.99,
    'currency': 'EUR',
    'license': 'OPL-1',
    'images': ['static/description/main_screenshot.png'],
    'depends': [
        'web',
    ],
    'data': [
    ],
    'qweb': [
        'static/src/xml/list_view_ext.xml',
    ],
}
