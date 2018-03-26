# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2017 brain-tec AG (http://www.braintec-group.com)
#    All Right Reserved
#
#    See LICENSE file for full licensing details.
##############################################################################

from odoo import models, fields


class ImportDataMessage(models.Model):

    _name = 'import.data.message'

    setting_id = fields.Many2one('import.data.settings')

    message = fields.Char(string='Message')
