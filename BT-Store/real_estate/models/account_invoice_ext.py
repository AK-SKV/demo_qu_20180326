# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2017 brain-tec AG (http://www.braintec-group.com)
# All Right Reserved
#
# See LICENSE file for full licensing details.
##############################################################################

from odoo import models, fields


class AccountInvoiceExt(models.Model):
    _inherit = 'account.invoice'

    building_id = fields.Many2one('real_estate.building', string='Building')
