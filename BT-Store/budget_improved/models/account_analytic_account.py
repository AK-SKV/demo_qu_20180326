# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2017 brain-tec AG (http://www.braintec-group.com)
# All Right Reserved
#
# See LICENSE file for full licensing details.
##############################################################################

from odoo import api, fields, models


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    sale_order_ids = fields.One2many('sale.order', 'project_id', string='Sale Orders')
    account_invoice_line_ids = fields.One2many('account.invoice.line', 'account_analytic_id',
                                               string='Account invoice lines')
    total_amount_sales = fields.Float(compute='_compute_total_amount_sales', string="Total amount sales")
    total_amount_invoices = fields.Float(compute='_compute_total_amount_invoices', string="Total amount invoices")

    @api.multi
    @api.depends('sale_order_ids',
                 'sale_order_ids.state')
    def _compute_total_amount_sales(self):
        for analytic_account in self:
            total_amount_sales = 0
            for sale_order in analytic_account.sale_order_ids:
                if sale_order.state in ['sale', 'done']:
                    total_amount_sales += sale_order.amount_untaxed
            analytic_account.total_amount_sales = total_amount_sales

    @api.multi
    @api.depends('account_invoice_line_ids',
                 'account_invoice_line_ids.invoice_id',
                 'account_invoice_line_ids.invoice_id.state')
    def _compute_total_amount_invoices(self):
        for analytic_account in self:
            total_amount_invoices = 0
            for invoice_line in analytic_account.account_invoice_line_ids:
                if invoice_line.invoice_id.state in ['open', 'paid']:
                    total_amount_invoices += invoice_line.price_subtotal_signed
            analytic_account.total_amount_invoices = total_amount_invoices
