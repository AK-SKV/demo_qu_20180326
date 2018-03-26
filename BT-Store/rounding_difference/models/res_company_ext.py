# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2017 brain-tec AG (http://www.braintec-group.com)
# All Right Reserved
#
# See LICENSE file for full licensing details.
##############################################################################

from odoo import models, fields, api, exceptions


class ResCompany(models.Model):
    _inherit = 'res.company'
    
    rounding_difference_product_id = fields.Many2one('product.product', 
                                                     string="Rounding difference product", 
                                                     default=lambda self: self._default_rounding_difference_product_id())
    rounding_precision = fields.Float(string="Rounding precision", default=0.05)
    
    @api.constrains('rounding_precision')
    def _check_rounding_precision(self):
        if not (0.0 < self.rounding_precision < 1.0):
            raise exceptions.ValidationError("The rounding precision must be a number between 0.00 and 1.00")
        
    def _default_rounding_difference_product_id(self):
        try:
            rounding_difference_product = self.env.ref('rounding_difference.product_rounding_difference')
            if rounding_difference_product:
                return rounding_difference_product.id
        except:
            return False