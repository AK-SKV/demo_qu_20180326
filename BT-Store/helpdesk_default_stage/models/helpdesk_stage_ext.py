# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2017 brain-tec AG (http://www.braintec-group.com)
# All Right Reserved
#
# See LICENSE file for full licensing details.
##############################################################################

from odoo import models, fields, api


class HelpdeskStageExt(models.Model):
    _inherit = 'helpdesk.stage'

    default_stage = fields.Boolean(string='Default for new helpdesk teams',
                                   help='If this field is checked, this stage will be added automatically to new helpdesk teams.')

    @api.multi
    def unlink(self):
        if not self._context.get('dont_delete_stage', False):
            return super(HelpdeskStageExt, self).unlink()
        else:
            return
