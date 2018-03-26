# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2017 brain-tec AG (http://www.braintec-group.com)
#    All Right Reserved
#
#    See LICENSE file for full licensing details.
##############################################################################

from odoo import models, fields, _
import logging

_logger = logging.getLogger(__name__)


SOURCE_TYPE_SELECTION = [('char', 'Char'),
                         ('number', 'Number')]

DEST_TYPE_SELECTION = [('char', 'Char'),
                       ('number', 'Number'),
                       ('null', 'Null'),
                       ('eval', 'Eval')]

EXCEP_IMPORT_PYTHON_MODULE = _(u'Could not import module {module}: {error}')


class ImportDataObjectColumn(models.Model):

    _name = 'import.data.object.column'

    object_id = fields.Many2one('import.data.object')

    number = fields.Integer('Column Number (Starting By 0)')

    model_id = fields.Many2one('ir.model', related='object_id.model_id')

    is_from_default = fields.Boolean(string='To Be Filled Automatically',
                                     help='Select this option if the value does not come from the file. Specify a '
                                          'default value')

    field_id = fields.Many2one('ir.model.fields', 'Field')

    type = fields.Selection(SOURCE_TYPE_SELECTION, string='Type')

    odoo_default_value = fields.Char('Odoo Default Value', help="If field is a m2o put the id of the record")

    defaults_only_on_create = fields.Boolean(string='Only On Create', help='Select this option if the default value is to be '
                                                                           'applied only on new records. '
                                                                           'Otherwise it will be applied also when updating '
                                                                           'already existing records')

    is_to_be_converted = fields.Boolean('Specify Values To Be Converted')

    source_type = fields.Selection(SOURCE_TYPE_SELECTION, 'Source Type')

    dest_type = fields.Selection(DEST_TYPE_SELECTION, 'Dest. Type')

    data_conversion_ids = fields.One2many('import.data.conversion', 'column_id',
                                          copy=True,
                                          string='Values To Be Converted')

    is_always_eval = fields.Boolean('Apply Same Expression Always')

    def converted_value(self, value):
        if not self.is_to_be_converted:
            return value
        else:
            _logger.info(_(u'The value {value} is being converted'.format(value=value)))
            new_value = unicode(value)

            if self.is_always_eval:
                convert_info_ids = self.data_conversion_ids
                source_value = new_value
            else:
                source_type = unicode if self.source_type == 'char' else float
                source_value = 'convert_info_ids[0].source_value'
                convert_info_ids = self.data_conversion_ids.filtered(lambda x: x.source_value
                                                                               == unicode(source_type(new_value)))
            if convert_info_ids:
                if self.dest_type == 'char':
                    new_value = unicode(convert_info_ids[0].dest_value)
                elif self.dest_type == 'number':
                    new_value = float(convert_info_ids[0].dest_value)
                elif self.dest_type == 'null':
                    new_value = None
                elif self.dest_type == 'eval':

                    # Import all necessary modules
                    for python_mod in convert_info_ids[0].python_module_ids:
                        try:
                            exec ('import {module}'.format(module=python_mod.name)) in locals()
                        except Exception as e:
                            _logger.warning(EXCEP_IMPORT_PYTHON_MODULE.format(module=python_mod.name,
                                                                              error=e))

                    # The user will refer to source_value as "source_value" in the GUI
                    expr = convert_info_ids[0].dest_value.replace('source_value',
                                                                  source_value)

                    new_value = eval(expr)
            _logger.info(_(u'The converted value is: {value}'.format(value=new_value)))
            return new_value
