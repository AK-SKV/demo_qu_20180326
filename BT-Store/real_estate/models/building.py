# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2017 brain-tec AG (http://www.braintec-group.com)
# All Right Reserved
#
# See LICENSE file for full licensing details.
##############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class Building(models.Model):
    _name = 'real_estate.building'
    _rec_name = 'display_name'
    _description = 'Building'
    _parent_store = True

    name = fields.Char(string='Description', required=True)
    display_name = fields.Char(string='Name', compute='_get_display_name', store=True)
    parent_id = fields.Many2one('real_estate.building', string='Building', index=True, ondelete='cascade')
    parent_left = fields.Integer(string='Left parent', index=True)
    parent_right = fields.Integer(string='Right parent', index=True)
    child_ids = fields.One2many('real_estate.building', 'parent_id', string='Child Tags')
    building_category_ids = fields.Many2many('real_estate.building.category',
                                             column1='building_id', column2='category_id', string='Tags')
    street = fields.Char(string='Street')
    street2 = fields.Char(string='Street 2')
    city = fields.Char(string='City')
    state_id = fields.Many2one('res.country.state', string='State')
    zip = fields.Char(string='ZIP')
    country_id = fields.Many2one('res.country', string='Country')
    contact_ids = fields.One2many('real_estate.building.contact', 'building_id', string='Contact')
    size = fields.Float(string='Size (m2)')
    sale_order_ids = fields.One2many('sale.order', 'building_id', string='Sales')
    sale_order_count = fields.Integer(compute='_get_sale_order_count')
    purchase_order_ids = fields.One2many('purchase.order', 'building_id', string='Purchases')
    purchase_order_count = fields.Integer(compute='_get_purchase_order_count')
    sale_subscription_ids = fields.One2many('sale.subscription', 'building_id', string='Subscriptions')
    sale_subscription_count = fields.Integer(compute='_get_sale_subscription_count')

    account_invoice_ids = fields.One2many('account.invoice', 'building_id', 'All Invoices')
    customer_invoice_ids = fields.One2many('account.invoice', compute='_compute_invoice_types',
                                           string='Customer Invoices')
    customer_invoice_count = fields.Integer(compute='_compute_invoice_types')
    customer_refund_ids = fields.One2many('account.invoice', compute='_compute_invoice_types',
                                          string='Customer Refunds')
    customer_refund_count = fields.Integer(compute='_compute_invoice_types')
    supplier_invoice_ids = fields.One2many('account.invoice', compute='_compute_invoice_types',
                                           string='Supplier Invoices')
    supplier_invoice_count = fields.Integer(compute='_compute_invoice_types')
    supplier_refund_ids = fields.One2many('account.invoice', compute='_compute_invoice_types',
                                          string='Supplier Refunds')
    supplier_refund_count = fields.Integer(compute='_compute_invoice_types')

    @api.multi
    @api.depends('name', 'parent_id')
    def _get_display_name(self):
        for building in self:
            if not building.parent_id:
                building.display_name = building.name
            else:
                building.display_name = '{0}, {1}'.format(building.parent_id.name, building.name)

    @api.onchange('parent_id')
    def onchange_parent_id(self):
        if self.parent_id:
            self.street = self.parent_id.street
            self.street2 = self.parent_id.street2
            self.city = self.parent_id.city
            self.state_id = self.parent_id.state_id
            self.zip = self.parent_id.zip
            self.country_id = self.parent_id.country_id

    @api.onchange('street', 'street2', 'city', 'state_id', 'zip', 'country_id')
    def onchange_address_values(self):
        vals_to_write = {
            'street': self.street,
            'street2': self.street2,
            'city': self.city,
            'zip': self.zip,
        }

        if self.state_id:
            vals_to_write['state_id'] = self.state_id.id

        if self.country_id:
            vals_to_write['country_id'] = self.country_id.id

        self.child_ids.write(vals_to_write)

    @api.constrains('parent_id')
    def _check_parent_id(self):
        if not self._check_recursion():
            raise ValidationError(_('Error ! You can not create recursive tags.'))

    @api.multi
    @api.depends('sale_order_ids')
    def _get_sale_order_count(self):
        for building in self:
            building.sale_order_count = len(building.sale_order_ids)

    @api.multi
    @api.depends('purchase_order_ids')
    def _get_purchase_order_count(self):
        for building in self:
            building.purchase_order_count = len(building.purchase_order_ids)

    @api.multi
    @api.depends('sale_subscription_ids')
    def _get_sale_subscription_count(self):
        for building in self:
            building.sale_subscription_count = len(building.sale_subscription_ids)

    @api.multi
    @api.depends('account_invoice_ids')
    def _compute_invoice_types(self):
        for building in self:
            customer_invoice_ids = []
            customer_refund_ids = []
            supplier_invoice_ids = []
            supplier_refund_ids = []
            for invoice in building.account_invoice_ids:
                if invoice.type == 'out_invoice':
                    customer_invoice_ids.append(invoice.id)
                elif invoice.type == 'in_invoice':
                    supplier_invoice_ids.append(invoice.id)
                elif invoice.type == 'out_refund':
                    customer_refund_ids.append(invoice.id)
                else:
                    supplier_refund_ids.append(invoice.id)
            building.customer_invoice_ids = customer_invoice_ids
            building.customer_invoice_count = len(customer_invoice_ids)

            building.customer_refund_ids = customer_refund_ids
            building.customer_refund_count = len(customer_refund_ids)

            building.supplier_invoice_ids = supplier_invoice_ids
            building.supplier_invoice_count = len(supplier_invoice_ids)

            building.supplier_refund_ids = supplier_refund_ids
            building.supplier_refund_count = len(supplier_refund_ids)
