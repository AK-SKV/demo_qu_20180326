# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2017 brain-tec AG (http://www.braintec-group.com)
# All Right Reserved
#
# See LICENSE file for full licensing details.
##############################################################################

from openerp import api, models
from openerp.http import request


class BaseModelExtend(models.AbstractModel):
    _name = 'basemodel.extend'

    def _register_hook(self):

        @api.model
        def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
            from user_agents import parse
            user_agent = parse(request.httprequest.user_agent.string)
            if not user_agent.is_pc:
                # Checking if there are any default view for mobiles
                view_reference = self.env['ir.ui.view'].sudo().search(
                    [('model', 'ilike', self._name),
                     ('is_for_mobiles', '=', True),
                     ('type', '=', view_type)],
                    limit=1)
                if view_reference:
                    view_id = view_reference.id
            res = models.BaseModel.fields_view_get.origin(self,
                                                          view_id=view_id,
                                                          view_type=view_type,
                                                          toolbar=toolbar,
                                                          submenu=submenu)
            return res

        if not hasattr(models.BaseModel.fields_view_get, 'origin'):
            models.BaseModel._patch_method('fields_view_get', fields_view_get)
        return super(BaseModelExtend, self)._register_hook()
