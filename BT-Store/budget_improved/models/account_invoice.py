# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2017 brain-tec AG (http://www.braintec-group.com)
# All Right Reserved
#
# See LICENSE file for full licensing details.
##############################################################################

from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    account_analytic_account_ids = fields.Many2many('account.analytic.account', string='Analytic accounts',
                                                    compute='_compute_account_analytic_account_ids',
                                                    search='_search_account_analytic_account_ids')

    @api.multi
    @api.depends('invoice_line_ids')
    def _compute_account_analytic_account_ids(self):
        account_analytic_account = self.env['account.analytic.account']
        for invoice in self:
            account_analytic_account_ids = set()
            for invoice_line in invoice.invoice_line_ids:
                if invoice_line.account_analytic_id:
                    account_analytic_account_ids.add(invoice_line.account_analytic_id.id)
            invoice.account_analytic_account_ids = account_analytic_account.browse(list(account_analytic_account_ids))

    def _search_account_analytic_account_ids(self, operator, value):
        return [('invoice_line_ids.account_analytic_id', operator, value)]
