# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2017 brain-tec AG (http://www.braintec-group.com)
# All Right Reserved
#
# See LICENSE file for full licensing details.
##############################################################################

from odoo import api, fields, models, _


class DataConversion(models.Model):
    """
    This class is intended to be used to cast/convert one or several possible values of a field
    into a different value. For example: 'Single' -> 'single' or 'one' -> 1 and so on.
    It also allows setting the value to NULL or even execute a python expression.
    """

    _name = 'import.data.conversion'

    column_id = fields.Many2one('import.data.object.column', string='Column')

    source_value = fields.Char('Source Value', help='Examples of numbers (both float and integers): '
                                                    '10.0, 0.0, 95.5, 1.0, 1.1. Never (1, 7, 6, etc)')

    dest_value = fields.Char(string='Dest. Value',
                             help='You can refer to Source Value as "source_value"')

    python_module_ids = fields.Many2many('python.module',
                                         'dataconversion_python_module_rel',
                                         'conversionobj_id',
                                         'pythonmod_id',
                                         string='Python Modules',
                                         help='Add here the python modules that you are going to need in your python '
                                              'expression')

    @api.multi
    def name_get(self):
        res = []
        for record in self:
            name = u'{0}{1}{2}'.format(unicode(record.source_value) if record.source_value else '',
                                       ': ' if record.source_value else '',
                                       record.dest_value)
            res.append((record.id, name))
        return res
