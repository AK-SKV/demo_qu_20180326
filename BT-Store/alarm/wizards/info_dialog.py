# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2017 brain-tec AG (http://www.braintec-group.com)
#    All Right Reserved
#
#    See LICENSE file for full licensing details.
##############################################################################

from odoo import api, fields, models, _


class InfoDialog(models.TransientModel):
    _name = 'alarm.info.dialog'
    _description = 'Alarm Info Dialog'

    # ======
    # FIELDS
    # ======

    message = fields.Text(_('Message'), readonly=True)

    # ===========
    # ORM METHODS
    # ===========

    @api.model
    def default_get(self, fields_list):
        defaults = super(InfoDialog, self).default_get(fields_list)

        if 'message' in fields_list :
            defaults['message'] = self.env.context.get('info_dialog_message', '')

        return defaults
