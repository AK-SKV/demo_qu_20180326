# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2017 brain-tec AG (http://www.braintec-group.com)
# All Right Reserved
#
# See LICENSE file for full licensing details.
##############################################################################

from odoo import api, fields, models, _


class StopSchedulersIrCronSettings(models.TransientModel):
    _inherit = 'base.config.settings'

    stop_schedulers_criteria = fields.Selection(
        [('no', 'No'),
         ('yes_indefinitely', 'Yes, indefinitely'),
         ('yes_until', 'Yes, until the moment indicated'),
         ], string='Stop Schedulers?', required=True, default='no',
        help="- No: The schedulers are not stopped and they run normally.\n"
             "- Yes, indefinitely: The schedulers are stopped until "
             "otherwise stated.\n"
             "- Yes, until the moment indicated: The schedulers are stopped "
             "until the indicated date & time is reached.")

    stop_schedulers_until = fields.Datetime("Date & Time")

    @api.multi
    def check_if_schedulers_can_run(self):
        """ Returns whether the schedulers can be executed.
        """
        ir_values_obj = self.env['ir.values']
        stop_schedulers_criteria = ir_values_obj.get_default(
            'base.config.settings', 'stop_schedulers_criteria')
        stop_schedulers_until = ir_values_obj.get_default(
            'base.config.settings', 'stop_schedulers_until')

        if stop_schedulers_criteria == 'no' or not stop_schedulers_criteria:
            # If the schedulers are not stopped, we can run them.
            schedulers_can_run = True

        elif stop_schedulers_criteria == 'yes_indefinitely':
            # If the schedulers are stopped indefinitely, we can not run them.
            schedulers_can_run = False

        elif stop_schedulers_criteria == 'yes_until':
            # If the schedulers are stopped until a date-time, then we
            # can run them only if we passed that moment in time.
            if fields.Datetime.now() < stop_schedulers_until:
                schedulers_can_run = False
            else:
                schedulers_can_run = True

        return schedulers_can_run

    @api.multi
    def set_stop_schedulers(self):
        """ Sets the values for the stopping of the schedulers.
        """
        self.ensure_one()
        ir_values_obj = self.env['ir.values']

        # If the 'yes_until' option is selected, then we must indicate also
        # a date & time to know until which moment the option applies.
        if self.stop_schedulers_criteria == 'yes_until' and \
           not self.stop_schedulers_until:
            error_msg = \
                _("Date & Time is required to know when the schedulers "
                  "will be able to execute again.")
            raise self.env['res.config.settings'].get_config_warning(error_msg)

        # The 'until' is cleared unless we have selected the correct option.
        stop_schedulers_until = False
        if self.stop_schedulers_criteria == 'yes_until':
            stop_schedulers_until = self.stop_schedulers_until

        ir_values_obj.sudo().set_default('base.config.settings',
                                         'stop_schedulers_criteria',
                                         self.stop_schedulers_criteria)
        ir_values_obj.sudo().set_default('base.config.settings',
                                         'stop_schedulers_until',
                                         stop_schedulers_until)

        return True
