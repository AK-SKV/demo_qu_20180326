# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2017 brain-tec AG (http://www.braintec-group.com)
# All Right Reserved
#
# See LICENSE file for full licensing details.
##############################################################################

from odoo import models, fields
from datetime import datetime, timedelta


class IrSequenceExt(models.Model):

    _inherit = 'ir.sequence'

    use_month_date_range = fields.Boolean('Use monthly subsequences per date_range', default=False)

    use_daily_date_range = fields.Boolean('Use daily subsequences per date_range', default=False)

    def _create_date_range_seq(self, date):
        """
        If the flag use_month_date_range is set, then new periods are opened on months
        """
        self.ensure_one()
        if not self.use_month_date_range and not self.use_daily_date_range:
            return super(IrSequenceExt, self)._create_date_range_seq(date)
        elif self.use_month_date_range:
            year = fields.Date.from_string(date).strftime('%Y')
            month = fields.Date.from_string(date).strftime('%m')
            date_from = '{}-{}-01'.format(year, month)
            if month == '12':
                month = 0
                year = int(year) + 1
            date_to = '{}-{}-01'.format(year, int(month) + 1)
            date_to = (datetime.strptime(date_to, '%Y-%m-%d') + timedelta(days=-1)).strftime('%Y-%m-%d')
            date_range = self.env['ir.sequence.date_range'].search([('sequence_id', '=', self.id),
                                                                    ('date_from', '>=', date),
                                                                    ('date_from', '<=', date_to)], order='date_from desc')
            if date_range:
                date_to = datetime.strptime(date_range.date_from, '%Y-%m-%d') + timedelta(days=-1)
                date_to = date_to.strftime('%Y-%m-%d')
            date_range = self.env['ir.sequence.date_range'].search([('sequence_id', '=', self.id),
                                                                    ('date_to', '>=', date_from),
                                                                    ('date_to', '<=', date)], order='date_to desc')
            if date_range:
                date_from = datetime.strptime(date_range.date_to, '%Y-%m-%d') + timedelta(days=1)
                date_from = date_from.strftime('%Y-%m-%d')
            seq_date_range = self.env['ir.sequence.date_range'].sudo().create({
                'date_from': date_from,
                'date_to': date_to,
                'sequence_id': self.id,
            })
            return seq_date_range
        elif self.use_daily_date_range:
            domain_search = []
            extra_month_dict = {}
            move_lines_month = self.env.context.get('move_lines_month', False)
            if move_lines_month:
                domain_search.extend([('extra_month_from', '=', move_lines_month),
                                      ('extra_month_to', '=', move_lines_month)])
                extra_month_dict = {'extra_month_from': move_lines_month,
                                    'extra_month_to': move_lines_month}
            year = fields.Date.from_string(date).strftime('%Y')
            month = fields.Date.from_string(date).strftime('%m')
            day = fields.Date.from_string(date).strftime('%d')
            date_from = '{}-{}-{}'.format(year, month, day)
            date_range = self.env['ir.sequence.date_range'].search(domain_search +
                                                                   [('sequence_id', '=', self.id),
                                                                    ('date_from', '>=', date_from),
                                                                    ('date_from', '<=', date_from)],
                                                                   order='date_from desc')
            if not date_range:
                values = {'date_from': date_from,
                          'date_to': date_from,
                          'sequence_id': self.id}
                values.update(extra_month_dict)
                date_range = self.env['ir.sequence.date_range'].sudo().create(values)
            return date_range

    def _next(self):
        """
        Overwrites the original method to filter also by month from move lines if specified in context.
        """
        dt = fields.Date.today()
        if self.env.context.get('ir_sequence_date'):
            dt = self.env.context.get('ir_sequence_date')
        domain_search = [('sequence_id', '=', self.id), ('date_from', '<=', dt), ('date_to', '>=', dt)]
        move_lines_month = self.env.context.get('move_lines_month', False)
        if move_lines_month:
            domain_search.extend([('extra_month_from', '=', move_lines_month),
                                  ('extra_month_to', '=', move_lines_month)])
        if not self.use_date_range:
            return self._next_do()
        seq_date = self.env['ir.sequence.date_range'].search(domain_search,limit=1)
        if not seq_date:
            seq_date = self._create_date_range_seq(dt)
        return seq_date.with_context(ir_sequence_date_range=seq_date.date_from)._next()
