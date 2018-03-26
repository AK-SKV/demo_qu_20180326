# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2017 brain-tec AG (http://www.braintec-group.com)
# All Right Reserved
#
# See LICENSE file for full licensing details.
##############################################################################

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ViewExt(models.Model):
    _inherit = 'ir.ui.view'

    is_for_mobiles = fields.Boolean(string="Should be used for mobiles?",
                                    help="Mark this field in order to use this view when accessing "
                                         "with mobiles to the model. Note that each model can only use a single view "
                                         "of each type for mobile devices.", default=False)

    @api.constrains('is_for_mobiles')
    def _check_id_for_mobiles(self):
        '''
        Checks if the model already has a default view for mobiles defined
        '''
        if self.is_for_mobiles:
            is_already_defined = self.search([('model', 'ilike', self.model),
                                              ('is_for_mobiles', '=', True),
                                              ('type', '=', self.type),
                                              ('id', 'not in', self.ids)],
                                             limit=1)
            if is_already_defined:
                raise ValidationError(_("There is already defined a default %(type)s view for the model %(model)s: "
                                        "%(defined_view_name)s") % ({'type': self.type,
                                                                     'model': self.model,
                                                                     'defined_view_name': is_already_defined.name,
                                                                     }))
