# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2017 brain-tec AG (http://www.braintec-group.com)
#    All Right Reserved
#
#    See LICENSE file for full licensing details.
##############################################################################

from odoo import api, models, fields
from . import import_object
import re


def generate_key_for_simple_fields(local_dict, keys):
    return local_dict.get(keys[0], False)


def clean_unicode(value):
    if isinstance(value, float):
        new_value = str(int(value))
    elif isinstance(value, int):
        new_value = str(value)
    else:
        new_value = value
    result = re.sub(' *$', '', new_value)
    result = re.sub(' +', ' ', result)
    return result


def generate_key_for_complex_fields(local_dict, keys):
    fields_list = [unicode(local_dict.get(x, '')) for x in keys]
    key = u' '.join(fields_list) if any(fields_list) else ''
    return clean_unicode(key)


TYPES_MAP = {'char': unicode,
             'number': float}


REL_FIELD_SELECTION = [('one2many', 'One2many'),
                       ('many2one', 'Many2one'),
                       ('many2many', 'Many2many'),]


class ImportDataObject(models.Model):

    _name = 'import.data.object'

    setting_id = fields.Many2one('import.data.settings')

    model_id = fields.Many2one('ir.model', 'Odoo Model')

    primary_key_ids = fields.Many2many('ir.model.fields',
                                       help='Set of fields that, together, define a unique identifier for a record')

    parent_id = fields.Many2one('import.data.object', 'Parent Object')

    rel_field_type = fields.Selection(REL_FIELD_SELECTION, 'Type Of Relation')

    rel_field_id = fields.Many2one('ir.model.fields', 'Relation Field')

    ttype = fields.Selection(related='rel_field_id.ttype', readonly=True)

    m2o_field_id = fields.Many2one('ir.model.fields', 'm2o Relation Field (Only if Rel. Field is One2many')

    column_ids = fields.One2many('import.data.object.column', 'object_id',
                                 copy=True,
                                 string='Columns')

    child_ids = fields.One2many('import.data.object', 'parent_id',
                                copy=True,
                                string='Related Objects')

    is_to_be_used_as_key = fields.Boolean(string='Use As Key For The Parent Object')

    @api.onchange('rel_field_type')
    def _onchange_rel_field_type(self):
        self.ensure_one()
        domain_dict = dict()
        if self.parent_id and self.parent_id.model_id:
            domain_dict['rel_field_id'] = [('model_id', '=', self.parent_id.model_id.id)]
        if self.model_id:
            domain_dict['m2o_field_id'] = [('model_id', '=', self.model_id.id)]
        return {'domain': domain_dict}

    def _get_conversion_function(self, column):

        def conversion_function(source_value):
            return column.converted_value(source_value)

        return conversion_function

    def create_import_object(self, parent=None):

        # Prepares columns names and types dictionaries
        columns = {x.number: x.field_id.name
                   for x in self.column_ids.filtered(lambda x: x.number and not x.is_from_default)}
        column_types = dict()
        column_defaults = dict()
        column_apply_defaults = dict()
        for x in self.column_ids:

            # Set types
            # If it comes exclusively from a default value the type is not needed
            if not x.is_from_default:
                if not x.is_to_be_converted:
                    column_types[x.field_id.name] = TYPES_MAP.get(x.type)
                else:
                    conv_function = self._get_conversion_function(x)
                    column_types[x.field_id.name] = conv_function

            # Set defaults
            if x.odoo_default_value:
                if x.field_id.ttype in ('many2one', 'many2many'):

                    # A list is expected in char format (i.e. '[1,2]')
                    default_value = eval(x.odoo_default_value)
                else:
                    default_value = x.odoo_default_value
                column_defaults[x.field_id.name] = default_value

                # Set if default fields are to be applied only on creation
                column_apply_defaults[x.field_id.name] = x.defaults_only_on_create


        # Primary key
        pk = self.primary_key_ids.mapped('name')

        # Key for generating a unique key out of the specified field(s)
        if len(pk) == 1:
            key_method = generate_key_for_simple_fields
        else:
            key_method = generate_key_for_complex_fields

        # Creates import_object
        new_import_object = import_object.ImportObject(columns,
                                                       column_types,
                                                       column_defaults,
                                                       column_apply_defaults,
                                                       self.model_id.model,
                                                       pk,
                                                       key_method,
                                                       parent,
                                                       self.rel_field_id.name,
                                                       self.m2o_field_id.name,
                                                       self.is_to_be_used_as_key)
        for object in self.child_ids:
            object.create_import_object(new_import_object)

        return new_import_object

    @api.multi
    @api.depends('model_id')
    def name_get(self):
        result = []
        for record in self:
            if record.model_id:
                result.append((record.id, '{desc}'.format(desc=record.model_id.name)))
        return result
