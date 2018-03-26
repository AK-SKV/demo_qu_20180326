# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2017 brain-tec AG (http://www.braintec-group.com)
# All Right Reserved
#
# See LICENSE file for full licensing details.
##############################################################################

from openerp import models, fields, api, tools, _
from odoo.exceptions import AccessError


class IrModelAccessExt(models.Model):
    _inherit = 'ir.model.access'

    @api.model
    @tools.ormcache_context('self._uid', 'model', 'mode', 'raise_exception', keys=('lang',))
    def check(self, model, mode='read', raise_exception=True):
        # We have to copy the sanity checks of the super function
        if self._uid == 1:
            # User root have all accesses
            return True

        assert mode in ('read', 'write', 'create', 'unlink'), 'Invalid access mode'

        if isinstance(model, models.BaseModel):
            assert model._name == 'ir.model', 'Invalid model object'
            model_name = model.model
        else:
            model_name = model

        # TransientModel records have no access rights, only an implicit access rule
        if model_name not in self.env:
            _logger.error('Missing model %s', model_name)
        elif self.env[model_name].is_transient():
            return True

        # Read-only user functionality
        if mode != 'read' and model != 'res.users.log':
            query = "SELECT is_regular_user FROM res_users WHERE id = {uid}".format(uid=self._uid)
            self._cr.execute(query)
            is_regular_user = self._cr.fetchone()[0]
            if not is_regular_user:
                if raise_exception:
                    raise AccessError(_("Sorry, you are read-only user."))
                else:
                    return False

        return super(IrModelAccessExt, self).check(model, mode, raise_exception)




