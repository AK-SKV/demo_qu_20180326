# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2017 brain-tec AG (http://www.braintec-group.com)
#    All Right Reserved
#
#    See LICENSE file for full licensing details.
##############################################################################

{
    'name': 'Alarms / Reminders',
    'summary': '''Create alarms for any record and send reminders to the appropriate users''',
    'author': 'brain-tec',
    'website': 'http://www.braintec-group.com/',
    'category': 'Extra Tools',
    'version': '10.0.1.0.0',
    'price': 30.0,
    'currency': 'EUR',
    'license': 'OPL-1',
    'images': ['static/description/main_screenshot.png'],
    'description': '''
Create an alarm for any record model, specify when the alarm should generate notifications and which
users are to be notified.

For example, we can create the following alarm:
 - Record model? Project Task
 - When must the alarm generate notifications? Two days before the deadline of the task
 - Which user(s) are to be notified? The user responsible for the task

As a result, each project task with a deadline taking place in 2 days will trigger the generation of an
alarm notification (a reminder) for the user that is set as responsible within the task. Note that the
user can access the task directly from the notification.''',
    'depends': ['mail'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',

        'wizards/notification_message_preview.xml',
        'wizards/info_dialog.xml',

        'views/alarm.xml',
        'views/notification.xml',
        'views/menu.xml',

        'data/cron.xml',
    ],
    'installable': True,
    'application': True,
}
