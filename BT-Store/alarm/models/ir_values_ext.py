# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2017 brain-tec AG (http://www.braintec-group.com)
#    All Right Reserved
#
#    See LICENSE file for full licensing details.
##############################################################################

from odoo import api, models, tools


class IrValuesExt(models.Model):
    _inherit = 'ir.values'

    @api.model
    @tools.ormcache_context('self._uid', 'action_slot', 'model', 'res_id', keys=('lang',))
    def get_actions(self, action_slot, model, res_id=False):
        actions = super(IrValuesExt, self).get_actions(action_slot, model, res_id=res_id)

        if (action_slot == 'client_action_multi' and model not in ('alarm.alarm', 'alarm.notification') and
            self.env['res.users'].has_group('alarm.group_alarm_user')):
            alarm_action = self.env['ir.model.data'].xmlid_to_object('alarm.create_alarm_for_current_object_action')
            alarm_fields = [field for field in alarm_action._fields]

            try:
                alarm_action_def = {
                    field: alarm_action._fields[field].convert_to_read(alarm_action[field], alarm_action)
                    for field in alarm_fields
                }

                actions.append((False, False, alarm_action_def))
            except Exception as e:
                pass

        return actions
