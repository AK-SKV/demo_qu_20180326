# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2017 brain-tec AG (http://www.braintec-group.com)
# All Right Reserved
#
# See LICENSE file for full licensing details.
##############################################################################

{
    'name': "Sequence based on month or day",
    'summary': "If a ir.sequence is date dependent, the sequence can now be reset by month and also by day.",
    'author': "brain-tec",
    'website': 'http://www.braintec-group.com',
    'category': 'Extra Tools',
    'version': '10.0.1.0.0',
    'price': '9.99',
    'currency': 'EUR',
    'license': 'OPL-1',
    'images': [
        'static/description/extended_sequence.png'
    ],
    'depends': ['base'],
    'data': [
             'views/ir_sequence_view.xml',
             ],
    'qweb': [
    ],
    'test': [
    ],
    'js': [
    ],
    'external_dependencies': {
    }
}