# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2017 brain-tec AG (http://www.braintec-group.com)
#    All Right Reserved
#
#    See LICENSE file for full licensing details.
##############################################################################
{
    'name': "Data File Importer",
    'summary': "Import Data From .xls(x) And .csv Files As Odoo Records",
    'author': "brain-tec",
    'website': 'http://www.braintec-group.com',
    'category': 'Extra Tools',
    'version': '10.0',
    'price': '599.99',
    'currency': 'EUR',
    'license': 'OPL-1',
    'images': [
        'static/description/file_data_importer.png'
    ],
    'depends': [
        'base',
    ],
    'data': [
        'views/import_data_settings_views.xml',
        'views/import_data_object_views.xml',
        'views/import_data_object_column_views.xml',
        'views/import_data_conversion_view.xml',
        'security/ir.model.access.csv',
    ],
    'external_dependencies': {
        'python': [
            'xlrd',
            'csv',
        ],
    },
    'qweb': [
    ],
    'test': [
    ],
    'js': [
    ]
}
