# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2017 brain-tec AG (http://www.braintec-group.com)
#    All Right Reserved
#
#    See LICENSE file for full licensing details.
##############################################################################

from odoo import api, fields, models, _

from datetime import date, timedelta


class Notification(models.Model):
    _name = 'alarm.notification'
    _description = 'Alarm Notification'
    _order = 'active_from DESC, model_id ASC, name ASC'

    # ======
    # FIELDS
    # ======

    alarm_id = fields.Many2one('alarm.alarm', _('Triggered Alarm'), required=True, readonly=True)
    name = fields.Char(_('Name'), size=256, required=True, readonly=True)
    user_id = fields.Many2one('res.users', _('Generated for'), required=True, readonly=True)
    model_id = fields.Many2one('ir.model', _('Model'), required=True, readonly=True)
    active_from = fields.Date(_('Active from'), required=True, default=fields.Date.today())
    record = fields.Reference([('x', 'x')], string=_('Record'), required=True, readonly=True)
    notification_message = fields.Text(_('Notification Message'), readonly=True)
    notes = fields.Text(_('Notes'))
    state = fields.Selection([('open', _('Open')),
                              ('closed', _('Closed')),
                              ('cancelled', _('Cancelled'))], _('State'), required=True)
    hash = fields.Text(_('Hash'))  # The goal of this hash is to avoid duplicates

    # ===========
    # ORM METHODS
    # ===========

    @api.model
    def create_ignoring_duplicates(self, values):
        new_id = False

        # Generates a "hash" for the new notification
        alarm_id = values.get('alarm_id')
        user_id = values.get('user_id')
        record_str = values.get('record')

        alarm = self.env['alarm.alarm'].browse(alarm_id)

        record_model, record_id_str = record_str.split(',')
        record = self.env[record_model].browse(int(record_id_str))
        record_date = record[alarm.date_field_id.name]

        new_hash = '{0}#{1}#{2}#{3}#{4}#{5}'.format(alarm_id,
                                                    alarm.date_field_id.name,
                                                    alarm.date_number,
                                                    user_id,
                                                    record_str,
                                                    record_date)

        # If the hash is not unique, then the notification is a duplicate and is ignored
        num_duplicated_notifications = self.search([('hash', '=', new_hash)], count=True)

        if not num_duplicated_notifications:
            values['hash'] = new_hash
            new_id = self.create(values)

        return new_id

    # ============
    # CRON METHODS
    # ============

    def cron_delete(self, num_days):
        if num_days > 0:
            deletion_date = date.today() - timedelta(days=num_days)

            notifications = self.search([('state', 'in', ('closed', 'cancelled')),
                                         ('active_from', '<', deletion_date)])

            notifications.unlink()
