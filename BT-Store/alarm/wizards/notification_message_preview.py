# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2017 brain-tec AG (http://www.braintec-group.com)
#    All Right Reserved
#
#    See LICENSE file for full licensing details.
##############################################################################

from odoo import api, fields, models, _


# noinspection PyRedundantParentheses
class NotificationMessagePreview(models.TransientModel):
    _name = 'alarm.notification.message.preview'
    _description = 'Notification Message Preview'

    # ===============================
    # FUNCTIONS FOR FIELD DEFINITIONS
    # ===============================

    def _sel_res_id_to_preview(self):
        model_to_preview = self.env.context.get('default_model_to_preview')

        if not model_to_preview:
            return []

        records = self.env[model_to_preview].search([], limit=10)
        return records.name_get()

    # ======
    # FIELDS
    # ======

    model_to_preview = fields.Char(_('Model to Preview'), size=128, readonly=True)
    res_id_to_preview = fields.Selection(_sel_res_id_to_preview, _('Record to Preview'))
    notification_message = fields.Text(_('Notification Message'))
    preview = fields.Text(_('Preview'), readonly=True)

    # ===========
    # ORM METHODS
    # ===========

    @api.model
    def default_get(self, fields_list):
        defaults = super(NotificationMessagePreview, self).default_get(fields_list)

        if 'res_id_to_preview' in fields_list and not defaults.get('res_id_to_preview'):
            records = self._sel_res_id_to_preview()
            defaults['res_id_to_preview'] = records and records[0][0] or False

        return defaults

    # ================
    # ONCHANGE METHODS
    # ================

    @api.onchange('res_id_to_preview')
    def onchange_record_to_preview(self):
        email_template_obj = self.env['mail.template']
        if self.notification_message and self.model_to_preview and self.res_id_to_preview:
            self.preview = email_template_obj.render_template(self.notification_message, self.model_to_preview,
                                                              [self.res_id_to_preview])[self.res_id_to_preview]