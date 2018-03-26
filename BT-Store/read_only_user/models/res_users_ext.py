# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2017 brain-tec AG (http://www.braintec-group.com)
# All Right Reserved
#
# See LICENSE file for full licensing details.
##############################################################################

from openerp import models, fields, api


class ResUsersExt(models.Model):
    _inherit = 'res.users'

    is_regular_user = fields.Boolean(string="Is Regular User", default=True)

    @api.one
    def toggle_regular_user(self):
        self.is_regular_user = not self.is_regular_user
