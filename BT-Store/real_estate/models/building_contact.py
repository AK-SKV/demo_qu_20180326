# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2017 brain-tec AG (http://www.braintec-group.com)
# All Right Reserved
#
# See LICENSE file for full licensing details.
##############################################################################

from odoo import models, fields, _


class BuildingContact(models.Model):
    _name = 'real_estate.building.contact'
    _description = 'Building Contact'

    building_id = fields.Many2one('real_estate.building', required=True, string='Building')
    partner_id = fields.Many2one('res.partner', required=True, domain=[('real_estate', '=', True)], string='Partner')
    type = fields.Selection([('bes', _('Owner')),
                             ('mie', _('Renter')),
                             ('abw', _('Caretaker'))], required=True, string='Type')
