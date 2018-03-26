# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2017 brain-tec AG (http://www.braintec-group.com)
# All Right Reserved
#
# See LICENSE file for full licensing details.
##############################################################################

from odoo import api, models
from odoo.tools import float_is_zero


class CrossoveredBudgetLines(models.Model):
    _inherit = "crossovered.budget.lines"

    @api.multi
    def _compute_practical_amount(self):
        res = super(CrossoveredBudgetLines, self)._compute_practical_amount()
        recs_to_recalculate = []
        for rec_to_check in self:
            if float_is_zero(rec_to_check.practical_amount, precision_rounding=0.01):
                recs_to_recalculate.append(rec_to_check)
        for line in recs_to_recalculate:
            acc_ids = line.general_budget_id.account_ids.ids
            date_to = self.env.context.get('wizard_date_to') or line.date_to
            date_from = self.env.context.get('wizard_date_from') or line.date_from
            if not line.analytic_account_id:
                self.env.cr.execute("""
                                SELECT COALESCE(SUM(debit), 0.0), COALESCE(SUM(credit), 0.0)
                                FROM account_move_line
                                WHERE (date between to_date(%s,'yyyy-mm-dd') AND to_date(%s,'yyyy-mm-dd'))
                                    AND account_id=ANY(%s)""",
                                    (date_from, date_to, acc_ids,))
                result = self.env.cr.fetchone()
                if result:
                    result_debit = result[0]
                    result_credit = result[1]
                    line.practical_amount = result_credit - result_debit
        return res
