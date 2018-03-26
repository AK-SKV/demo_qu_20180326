# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2017 brain-tec AG (http://www.braintec-group.com)
# All Right Reserved
#
# See LICENSE file for full licensing details.
##############################################################################

from openerp import models, api
import logging


_logger = logging.getLogger(__name__)


class IrCronExt(models.Model):
    _inherit = 'ir.cron'

    @api.model
    def _callback(self, model_name, method_name, args, job_id):
        """ Overridden so that we can skip the execution of a scheduler.
        
            This checks if according to the configuration set for
            the app Stop Schedulers, the execution of the schedulers
            has to be skipped. If that is the case, it logs (at log level INFO)
            that the execution of the scheduler was skipped. Otherwise it
            just executes normally.
        """
        settings_obj = self.env['base.config.settings']
        schedulers_can_run = settings_obj.check_if_schedulers_can_run()
        if schedulers_can_run:
            return super(IrCronExt, self)._callback(
                model_name, method_name, args, job_id)

        else:
            if _logger.isEnabledFor(logging.INFO):
                _logger.info('Scheduler {sched_name} was skipped on purpose '
                             'because of the configuration set for the app '
                             'Stop Schedulers.'.format(sched_name=self.name))
