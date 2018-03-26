# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2017 brain-tec AG (http://www.braintec-group.com)
# All Right Reserved
#
# See LICENSE file for full licensing details.
##############################################################################

from odoo import models, fields, api


class HelpdeskTeamExt(models.Model):
    _inherit = 'helpdesk.team'

    def _get_default_stages(self):
        return self.env['helpdesk.stage'].search([('default_stage', '=', True)])

    stage_ids = fields.Many2many('helpdesk.stage', relation='team_stage_rel', string='Stages',
                                 default=_get_default_stages,
                                 help="Stages the team will use. This team's tickets will only be able to be in these stages.")

    @api.multi
    def unlink(self):
        return super(HelpdeskTeamExt, self.with_context(dont_delete_stage=True)).unlink()
