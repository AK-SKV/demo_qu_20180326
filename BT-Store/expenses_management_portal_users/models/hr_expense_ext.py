# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2017 brain-tec AG (http://www.braintec-group.com)
# All Right Reserved
#
# See LICENSE file for full licensing details.
##############################################################################

from odoo import api, fields, models


class HrExpenseExt(models.Model):
    _inherit = 'hr.expense'

    last_refused_message = fields.Html(compute='_compute_last_refused_message')

    @api.multi
    def _compute_last_refused_message(self):
        for expense in self:
            if expense.sheet_id and expense.sheet_id.message_ids:
                messages = expense.sheet_id.sudo().message_ids.filtered(
                    lambda r: r.body and 'has been refused' in r.body).sorted('date', reverse=True)
                if messages:
                    expense.last_refused_message = messages[0].body
