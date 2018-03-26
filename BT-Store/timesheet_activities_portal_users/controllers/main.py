# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2017 brain-tec AG (http://www.braintec-group.com)
# All Right Reserved
#
# See LICENSE file for full licensing details.
##############################################################################

from collections import OrderedDict
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo import http, _
from odoo.http import request
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

from odoo.addons.website_portal.controllers.main import website_account


class WebsiteAccount(website_account):

    MANDATORY_BILLING_FIELDS = ["name", "project_id", "date"]
    OPTIONAL_BILLING_FIELDS = ["task_id", "unit_amount"]

    @http.route(['/my/timesheet_activities', '/my/timesheet_activities/page/<int:page>'],
                type='http', auth="user", website=True)
    def my_timesheet_activities(self, page=1, date=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        account_analytic_line = request.env['account.analytic.line']

        sortings = {
            'date': {'label': _('Newest'), 'order': 'date desc'},
            'name': {'label': _('Name'), 'order': 'name'},
        }

        user_id = values.get('user', 0)
        if user_id != 0:
            user_id = user_id.id
        domain = [('user_id', '=', user_id),
                  ('project_id', '!=', False)]
        today_date = fields.Date.from_string(fields.Date.today())
        yesterday = fields.Date.to_string(today_date - timedelta(days=1))
        this_mon = fields.Date.to_string(today_date - relativedelta(days=today_date.weekday()))
        this_sun = fields.Date.to_string(today_date + relativedelta(days=7 - today_date.weekday() - 1))
        this_month_start = fields.Date.to_string(today_date - timedelta(days=today_date.day-1))
        this_month_end = fields.Date.to_string(today_date + relativedelta(months=1) - timedelta(days=today_date.day))
        date_filters = {
            'all': {'label': _('All'), 'domain': domain},
            'today': {'label': _('Today'), 'domain': domain + [('date', '=', fields.Date.today())]},
            'yesterday': {'label': _('Yesterday'), 'domain': domain + [('date', '=', yesterday)]},
            'this_week': {'label': _('This Week'), 'domain': domain + [('date', '>=', this_mon),
                                                                       ('date', '<=', this_sun)]},
            'this_month': {'label': _('This Month'), 'domain': domain + [('date', '>=', this_month_start),
                                                                         ('date', '<=', this_month_end)]},
        }

        order = sortings.get(sortby, sortings['date'])['order']
        if date_filters.get(date, None):
            domain += date_filters.get(date, None)['domain']

        # archive groups - Default Group By 'create_date'
        archive_groups = self._get_archive_groups('account.analytic.line', domain)

        my_timesheets_count = account_analytic_line.search_count(domain)
        values.update({
            'my_timesheets_count': my_timesheets_count,
        })
        # pager
        pager = request.website.pager(
            url="/my/timesheet_activities",
            url_args={'date': date, 'sortby': sortby},
            total=values['my_timesheets_count'],
            page=page,
            step=self._items_per_page
        )

        # content according to pager and archive selected
        timesheet_activities = account_analytic_line.sudo().search(domain, order=order,
                                                                 limit=self._items_per_page, offset=pager['offset'])

        values.update({
            'date': date,
            'date_filters': OrderedDict(sorted(date_filters.items())),
            'sortings': sortings,
            'sortby': sortby,
            'timesheet_activities': timesheet_activities,
            'page_name': 'timesheet_activity',
            'archive_groups': archive_groups,
            'default_url': '/my/timesheet_activities',
            'pager': pager,
            'convert_date': self.convert_date,
            'translate_func': _,
        })
        return request.render("timesheet_activities_portal_users.my_timesheet_activities", values)

    def convert_date(self, date):
        lang = request.env['res.lang'].search([('code', 'like', request.httprequest.cookies.get('website_lang'))], limit=1)
        date_str = ""
        if date:
            date_str = datetime.strptime(date, DEFAULT_SERVER_DATE_FORMAT).strftime(lang.date_format)

        return date_str

    @http.route(['/my/timesheet_activity/update'],
                type='http', auth="public", methods=['POST'], website=True, csrf=False)
    def timesheet_update(self, timesheet_activity_id, project_id, date,
                         name, task_id=False, unit_amount=0, to_delete=False, **kw):
        if to_delete:
            return request.redirect("/my/timesheet_activity/delete/%s" % (timesheet_activity_id,))
        lang = request.env['res.lang'].search([('code', 'like', request.httprequest.cookies.get('website_lang'))],
                                              limit=1)
        values = {
            'project_id': int(project_id) if project_id else False,
            'date': date,
            'name': name,
            'task_id': int(task_id) if task_id else False,
            'unit_amount': unit_amount,
        }
        error, error_message, date_parsed = self.my_timesheet_activity_form_validate(values, lang)
        if not error:
            if date_parsed is not None:
                date_parsed = date_parsed.strftime(DEFAULT_SERVER_DATE_FORMAT)
                values.update({
                    'date': date_parsed,
                })
            if timesheet_activity_id:
                timesheet_activity_id = int(timesheet_activity_id)
                vals_to_write = dict(values)
                request.env['account.analytic.line'].sudo().browse(timesheet_activity_id).write(vals_to_write)
            else:
                values.update({
                    'user_id': request.env.uid,
                })
                request.env['account.analytic.line'].sudo().create(values)
            return request.redirect("/my/timesheet_activities")
        else:
            values.update({
                'error': error,
                'error_message': error_message,
            })
            projects = request.env['project.project'].search([])
            tasks = request.env['project.task'].search([])

            values.update({
                'projects': projects,
                'tasks': tasks,
            })
            if timesheet_activity_id:
                timesheet_activity_id = int(timesheet_activity_id)
                values.update({
                    'timesheet_activity': request.env['account.analytic.line'].sudo().browse(timesheet_activity_id),
                })
            return request.render("timesheet_activities_portal_users.my_timesheet_activity", values)

    @http.route(['/my/timesheet_activity/<model("account.analytic.line"):timesheet_activity>',
                 '/my/timesheet_activity/create'],
                type='http', auth="user", website=True)
    def my_timesheet_activity(self, timesheet_activity=None, **kwargs):

        values = {
            'error': {},
            'error_message': []
        }
        projects = request.env['project.project'].search([])
        tasks = request.env['project.task'].search([])
        lang = request.env['res.lang'].search([('code', 'like', request.httprequest.cookies.get('website_lang'))],
                                              limit=1)

        values.update({
            'projects': projects,
            'tasks': tasks,
            'timesheet_activity': timesheet_activity,
        })
        if timesheet_activity:
            my_date = datetime.strptime(timesheet_activity.date, DEFAULT_SERVER_DATE_FORMAT).strftime(lang.date_format)
        else:
            my_date = datetime.strptime(fields.Date.today(), DEFAULT_SERVER_DATE_FORMAT).strftime(lang.date_format)
        values['date'] = my_date

        return request.render("timesheet_activities_portal_users.my_timesheet_activity", values)

    def my_timesheet_activity_form_validate(self, data, lang):
        error = dict()
        error_message = []

        unit_amount = data.get('unit_amount', None)
        if unit_amount:
            try:
                unit_amount = float(unit_amount) if unit_amount else 0.0
                data['unit_amount'] = unit_amount
            except ValueError:
                error['unit_amount'] = "wrong unit_amount"
                error_message.append("Duration of the timesheet must be a number.")

        date = data.get('date', None)
        date_parsed = None
        if date:
            try:
                date_parsed = datetime.strptime(date, lang.date_format)
                date_parsed = date_parsed.date()
            except ValueError:
                error['date'] = "not date"
                error_message.append("Your date should have the following format: '%s'" % (lang.date_format,))

        # Validation
        for field_name in self.MANDATORY_BILLING_FIELDS:
            if not data.get(field_name):
                error[field_name] = 'missing'

        # error message for empty required fields
        if [err for err in error.values() if err == 'missing']:
            error_message.append(_('Some required fields are empty.'))

        unknown = [k for k in data.iterkeys() if k not in self.MANDATORY_BILLING_FIELDS + self.OPTIONAL_BILLING_FIELDS]
        if unknown:
            error['common'] = 'Unknown field'
            error_message.append("Unknown field '%s'" % ','.join(unknown))

        return error, error_message, date_parsed

    @http.route(['/my/timesheet_activity/delete/<model("account.analytic.line"):timesheet_activity>',
                 '/my/timesheet_activity/delete'],
                type='http', auth="user", website=True)
    def delete_timesheet_activities(self, timesheet_activity=None, **kwargs):
        '''
        :param kwargs: ids of the timesheets to remove
        :return: redirection
        '''
        timesheets_to_delete = []
        if timesheet_activity:
            timesheet_activity.sudo().unlink()
        else:
            for timesheet_id in kwargs:
                if timesheet_id.isdigit() and kwargs[timesheet_id] == 'on':
                    timesheets_to_delete.append(int(timesheet_id))
            request.env['account.analytic.line'].sudo().browse(timesheets_to_delete).unlink()

        return request.redirect("/my/timesheet_activities")
