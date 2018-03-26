# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2017 brain-tec AG (http://www.braintec-group.com)
# All Right Reserved
#
# See LICENSE file for full licensing details.
##############################################################################

from odoo import models, fields, api
from odoo.tools import float_is_zero


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    
    @api.model
    def create(self, vals):
        ret = super(AccountInvoice, self).create(vals)
        ret._add_rounding_difference()
        return ret
 
    @api.multi
    def write(self, vals):            
        ret = super(AccountInvoice, self).write(vals)
        self._add_rounding_difference()
        return ret
    
    @api.multi
    def _add_rounding_difference(self):
        account_invoice_line_obj = self.env['account.invoice.line']

        for invoice in self:  
            if invoice.company_id:
                precision = invoice.company_id.rounding_precision
                product= invoice.company_id.rounding_difference_product_id
                if product and precision:
                    account_invoice_line = account_invoice_line_obj.search([('invoice_id', '=', invoice.id),
                                                                            ('product_id', '=', product.id)])
                    if account_invoice_line:
                            account_invoice_line.unlink()
                    
                    rounding_difference = self._compute_rounding_difference(invoice, precision)
                    if not rounding_difference == 0.0:
                        sequence = self._compute_sequence(invoice)
                        account_invoice_line_obj.create({'invoice_id': invoice.id,
                                                         'product_id': product.id,
                                                         'name': product.name,
                                                         'quantity': 1,
                                                         'price_unit': rounding_difference,
                                                         'account_id': product.property_account_income_id.id,
                                                         'sequence': sequence})
    
    def _compute_rounding_difference(self, invoice, precision):
        """
        Compute the rounding difference taking care of rounding
        CASE 1:
            If invoice amount is 19.95 and precision 0.05 there is no rounding difference
        CASE 2:
            If invoice amount is 19.97 and precision 0.05 rounding difference should be -0.02
        CASE 3:
            If invoice amount is 19.98 and precision 0.05 rounding difference should be +0.02
        """
        rounding_difference = invoice.amount_total % precision
        digits_rounding_precision =  invoice.currency_id.rounding
        if float_is_zero(rounding_difference, precision_rounding=digits_rounding_precision):
            return 0.0
        elif rounding_difference < precision / 2:
            return -1 * rounding_difference
        elif rounding_difference >= precision / 2:
            return precision - rounding_difference
        
    def _compute_sequence(self, invoice):
        """
        Returns the max sequence + 1
        Will allow us to place the rounding difference invoice line always at the end 
        """
        account_invoice_line_obj = self.env['account.invoice.line']
        account_invoice_lines = account_invoice_line_obj.search([('invoice_id', '=', invoice.id)])
        sequence = 0
        for invoice_line in account_invoice_lines:
            if invoice_line.sequence > sequence:
                sequence = invoice_line.sequence
                
        return sequence + 1