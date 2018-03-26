# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2017 brain-tec AG (http://www.braintec-group.com)
# All Right Reserved
#
# See LICENSE file for full licensing details.
##############################################################################

{
    'name': "Task Hierarchy",
    'summary': "Enables a user to create tasks inside other tasks in a nested way:"
               "sub-tasks can contain other sub-tasks and so on",
    'author': "brain-tec",
    'website': 'http://www.braintec-group.com',
    'category': 'Project',
    'version': '1.0',
    'price': '9.99',
    'currency': 'EUR',
    'license': 'OPL-1',
    'images': [
        'static/description/task_hierarchy.png'
    ],
    'depends': [
        'project',
    ],
    'data': [
        # VIEWS
        'views/project_task_view_ext.xml',
    ],
    'qweb': [],
    'test': [],
    'js': [],
}
