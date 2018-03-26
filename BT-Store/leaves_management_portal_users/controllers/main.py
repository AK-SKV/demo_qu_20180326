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
import pytz
from logging import getLogger

from odoo import fields
from odoo import http, _
from odoo.http import request
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import ValidationError

from odoo.addons.website_portal.controllers.main import website_account

_logger = getLogger(__name__)


class WebsiteAccount(website_account):

    @http.route(['/my/leaves', '/my/leaves/page/<int:page>'],
                type='http', auth="user", website=True)
    def my_leaves(self, page=1, date=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        user_id = values.get('user', 0)
        if user_id == 0 or not user_id.email:
            return request.render("leaves_management_portal_users.leaves_partner_with_no_mail")
        hr_holidays = request.env['hr.holidays']

        sortings = {
            'date_from': {'label': _('Newest'), 'order': 'date_from desc'},
            'name': {'label': _('Description'), 'order': 'name'},
        }

        if user_id != 0:
            user_id = user_id.id
        domain = [('user_id', '=', user_id), ('type', '=', 'remove')]
        today_date = fields.Datetime.from_string(fields.Datetime.now()).replace(hour=0, minute=0, second=0)
        this_mon = fields.Datetime.to_string(today_date - relativedelta(days=today_date.weekday()))
        this_sun = fields.Datetime.to_string(today_date + relativedelta(days=7 - today_date.weekday() - 1))
        this_month_start = fields.Datetime.to_string(today_date - timedelta(days=today_date.day - 1))
        this_month_end = fields.Datetime.to_string(
            today_date + relativedelta(months=1) - timedelta(days=today_date.day))
        date_filters = {
            'future_leaves': {'label': _('Future leaves'),
                              'domain': [('date_from', '>=', fields.Datetime.now())]},
            'this_week': {'label': _('This Week'), 'domain': [('date_from', '>=', this_mon),
                                                              ('date_from', '<=', this_sun)]},
            'this_month': {'label': _('This Month'), 'domain': [('date_from', '>=', this_month_start),
                                                                ('date_from', '<=', this_month_end)]},
            'all': {'label': _('All'), 'domain': []},
        }

        order = sortings.get(sortby, sortings['date_from'])['order']
        if date_filters.get(date, None):
            domain += date_filters.get(date, None)['domain']
        else:
            domain += date_filters.get('future_leaves')['domain']

        # archive groups - Default Group By 'create_date'
        archive_groups = self._get_archive_groups('hr.holidays', domain)
        my_leaves_count = hr_holidays.sudo().search_count(domain)
        values.update({
            'my_leaves_count': my_leaves_count,
        })
        # pager
        pager = request.website.pager(
            url="/my/leaves",
            url_args={'date_from': date, 'sortby': sortby},
            total=values['my_leaves_count'],
            page=page,
            step=self._items_per_page
        )

        # content according to pager and archive selected
        leaves = hr_holidays.sudo().search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])

        values.update({
            'date': date,
            'date_filters': OrderedDict(sorted(date_filters.items())),
            'sortings': sortings,
            'sortby': sortby,
            'leaves': leaves,
            'page_name': 'leave',
            'archive_groups': archive_groups,
            'default_url': '/my/leaves',
            'pager': pager,
            'convert_datetime_to_date': self.convert_datetime_to_date,
            'get_description_state_dict': self.get_description_state_dict(),
            'get_class_state_dict': self.get_class_state_dict(),
            'translate_func': _,
        })
        if request.session.get('error_unlink', None):
            if request.session.get('error_unlink_shown', None):
                del request.session['error_unlink']
                del request.session['error_unlink_shown']
            else:
                request.session['error_unlink_shown'] = True
        return request.render("leaves_management_portal_users.my_leaves", values)

    def is_morning(self, my_datetime):
        if len(my_datetime) > 10:
            my_datetime_datetime = fields.Datetime.from_string(my_datetime)
            my_datetime_datetime = self.leaves_context_timestamp(my_datetime_datetime,
                                                                 request.env.context,
                                                                 request.env.user.tz).strftime(
                DEFAULT_SERVER_DATETIME_FORMAT)
            my_datetime_datetime = fields.Datetime.from_string(my_datetime_datetime)
        else:
            my_datetime_datetime = fields.Date.from_string(my_datetime)
        aux = my_datetime_datetime.replace(hour=12, minute=0, second=0)
        if aux > my_datetime_datetime:
            ret = True
        else:
            ret = False
        return ret

    def convert_datetime_to_date(self, my_datetime):
        lang = request.env['res.lang'].search([('code', 'like', request.httprequest.cookies.get('website_lang')),
                                               ('date_format', '!=', False)],
                                              limit=1)
        if not lang:
            lang_date_format = DEFAULT_SERVER_DATE_FORMAT
        else:
            lang_date_format = lang.date_format
        date_str = ""
        if my_datetime:
            if len(my_datetime) > 10:
                date_str = datetime.strptime(my_datetime, DEFAULT_SERVER_DATETIME_FORMAT)
            else:
                date_str = datetime.strptime(my_datetime, DEFAULT_SERVER_DATE_FORMAT)
            date_str = self.leaves_context_timestamp(date_str, request.env.context, request.env.user.tz)
            date_str = date_str.strftime('%s' % (lang_date_format,))

        return date_str

    @staticmethod
    def leaves_context_timestamp(timestamp, context, user_tz):
        assert isinstance(timestamp, datetime), 'Datetime instance expected'
        tz_name = context.get('tz') or user_tz
        utc_timestamp = pytz.utc.localize(timestamp, is_dst=False)  # UTC = no DST
        if tz_name:
            try:
                context_tz = pytz.timezone(tz_name)
                return utc_timestamp.astimezone(context_tz)
            except Exception:
                _logger.debug("failed to compute context/client-specific timestamp, "
                              "using the UTC value",
                              exc_info=True)
        return utc_timestamp

    @staticmethod
    def get_description_state_dict():
        states = request.env['hr.holidays']._fields['state']._description_selection(request.env)
        dic_states = {}
        for st in states:
            dic_states[st[0]] = st[1]
        return dic_states

    @staticmethod
    def get_class_state_dict():
        '''
            ('draft', 'To Submit'),
            ('cancel', 'Cancelled'),
            ('confirm', 'To Approve'),
            ('refuse', 'Refused'),
            ('validate1', 'Second Approval'),
            ('validate', 'Approved')
        '''
        css_class_dict = {
            'draft': 'label label-warning',
            'confirm': 'label label-info',
            'cancel': 'label label-default',
            'refuse': 'label label-danger',
            'validate1': 'label label-success',
            'validate': 'label label-success',
        }
        return css_class_dict

    def on_update_error_leaves_portal(self, values, error, error_message, leave_id, date_from_half_day,
                                      date_to_half_day):
        values.update({
            'error': error,
            'error_message': error_message,
            'convert_datetime_to_date': self.convert_datetime_to_date,
            'get_description_state_dict': self.get_description_state_dict(),
            'get_class_state_dict': self.get_class_state_dict(),
        })

        user = request.env.user
        context = dict(request.env.context)
        if user.employee_ids:
            context['employee_id'] = user.employee_ids[0].id
        leave_types = request.env['hr.holidays.status'].with_context(context).search([])

        values.update({
            'holiday_status_ids': leave_types,
            'date_from_half_day': date_from_half_day,
            'date_to_half_day': date_to_half_day,
        })
        if leave_id:
            leave_id = int(leave_id)
            values.update({
                'leave': request.env['hr.holidays'].sudo().browse(leave_id),
            })
        return request.render("leaves_management_portal_users.my_leave", values)

    @http.route(['/my/leave/update'],
                type='http', auth="public", methods=['POST'], website=True, csrf=False)
    def leave_update(self, leave_id, holiday_status_id, date_from, date_to,
                     name, date_from_half_day, date_to_half_day, to_delete=False, **kw):
        if not request.env.user or not request.env.user.email:
            return request.render("leaves_management_portal_users.leaves_partner_with_no_mail")
        if to_delete:
            return request.redirect("/my/leave/delete/%s" % (leave_id,))
        lang = request.env['res.lang'].search([('code', 'like', request.httprequest.cookies.get('website_lang')),
                                               ('date_format', '!=', False)],
                                              limit=1)
        if not lang:
            lang_date_format = DEFAULT_SERVER_DATE_FORMAT
        else:
            lang_date_format = lang.date_format
        values = {
            'holiday_status_id': int(holiday_status_id) if holiday_status_id else False,
            'date_from': date_from,
            'date_to': date_to,
            'name': name,
        }
        error, error_message, date_from_parsed, date_to_parsed = self.my_leave_form_validate(values, lang)
        if not error:
            vals_to_write = dict(values)
            if date_from_parsed is not None:
                values.update({
                    'date_from': date_from_parsed.strftime(lang_date_format),
                })
                if date_from_half_day != 'morning':
                    date_from_parsed = date_from_parsed + timedelta(hours=12)
                vals_to_write.update({
                    'date_from': date_from_parsed.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                })
            if date_to_parsed is not None:
                values.update({
                    'date_to': date_to_parsed.strftime(lang_date_format),
                })
                if date_to_half_day == 'morning':
                    date_to_parsed = date_to_parsed + timedelta(hours=11, minutes=59, seconds=59)
                else:
                    date_to_parsed = date_to_parsed + timedelta(hours=23, minutes=59, seconds=59)
                vals_to_write.update({
                    'date_to': date_to_parsed.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                })
            if date_from_parsed and date_to_parsed:
                if date_from_parsed > date_to_parsed:
                    error['date_to'] = "wrong date_to"
                    error_message.append(_("The start date must be anterior to the end date."))
                    return self.on_update_error_leaves_portal(values, error, error_message, leave_id,
                                                              date_from_half_day, date_to_half_day)
            if leave_id:
                leave_id = int(leave_id)

                vals_to_write.update({'state': 'confirm'})
                try:
                    request.env['hr.holidays'].browse(leave_id).write(vals_to_write)
                except ValidationError as ve:
                    error['general'] = "Validation error"
                    error_message.append(ve.name)
                    return self.on_update_error_leaves_portal(values, error, error_message, leave_id,
                                                              date_from_half_day, date_to_half_day)
            else:
                if not request.env.user.employee_ids:
                    error['employee_id'] = "not employee_id set"
                    error_message.append(_("Please make sure that your user has an employee assigned "
                                           "(contact with the administrator)."))
                    return self.on_update_error_leaves_portal(values, error, error_message, leave_id,
                                                              date_from_half_day, date_to_half_day)
                # Compute and update the number of days
                number_of_days_temp = 0
                if (date_to_parsed and date_from_parsed) and (date_from_parsed <= date_to_parsed):
                    user = request.env.user
                    if user.employee_ids:
                        number_of_days_temp = request.env['hr.holidays'].sudo()._get_number_of_days(
                            date_from_parsed.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                            date_to_parsed.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                            user.employee_ids[0].id)
                        values.update({'employee_id': user.employee_ids[0].id})

                vals_to_write.update({
                    'user_id': request.env.uid,
                    'type': 'remove',
                    'number_of_days_temp': number_of_days_temp,
                })
                try:
                    current_last_holiday = request.env['hr.holidays'].search(
                        [('user_id', '=', request.env.uid),
                         ('type', '=', 'remove'),
                         ('number_of_days_temp', '=', number_of_days_temp),
                         ('create_date', '>=', fields.Date.today())],
                        order='id desc', limit=1)
                    request.env['hr.holidays'].create(vals_to_write)
                except ValidationError as ve:
                    exception_last_holiday = request.env['hr.holidays'].search(
                        [('user_id', '=', request.env.uid),
                         ('type', '=', 'remove'),
                         ('number_of_days_temp', '=', number_of_days_temp),
                         ('create_date', '>=', fields.Date.today())],
                        order='id desc', limit=1)
                    if current_last_holiday.id != exception_last_holiday.id:
                        # Hack esal1: SQL constraints are validated after the creation of the record
                        #             so if they fail, the record is already created and
                        #             if we handle the exception, it is not removed from the DB automatically
                        exception_last_holiday.sudo().unlink()
                    error['general'] = "Validation error"
                    error_message.append(ve.name)
                    return self.on_update_error_leaves_portal(values, error, error_message, leave_id,
                                                              date_from_half_day, date_to_half_day)
            return request.redirect("/my/leaves")
        else:
            return self.on_update_error_leaves_portal(values, error, error_message, leave_id,
                                                      date_from_half_day, date_to_half_day)

    @http.route(['/my/leave/<model("hr.holidays"):leave>',
                 '/my/leave/create'],
                type='http', auth="user", website=True)
    def my_leave(self, leave=None, **kwargs):

        values = {
            'error': {},
            'error_message': [],
            'convert_datetime_to_date': self.convert_datetime_to_date,
            'get_description_state_dict': self.get_description_state_dict(),
            'get_class_state_dict': self.get_class_state_dict(),
        }

        user = request.env.user
        if not user or not user.email:
            return request.render("leaves_management_portal_users.leaves_partner_with_no_mail")
        context = dict(request.env.context)
        if user.employee_ids:
            context['employee_id'] = user.employee_ids[0].id
        leave_types = request.env['hr.holidays.status'].with_context(context).search([])
        lang = request.env['res.lang'].search([('code', 'like', request.httprequest.cookies.get('website_lang')),
                                               ('date_format', '!=', False)],
                                              limit=1)
        if not lang:
            lang_date_format = DEFAULT_SERVER_DATE_FORMAT
        else:
            lang_date_format = lang.date_format

        values.update({
            'holiday_status_ids': leave_types,
            'leave': leave,
            'date_from_is_morning': self.is_morning(leave.date_from) if leave else False,
            'date_to_is_morning': self.is_morning(leave.date_to) if leave else False,
        })
        if leave:
            date_from_date_to_field_type = DEFAULT_SERVER_DATETIME_FORMAT if len(leave.date_from) > 10 else DEFAULT_SERVER_DATE_FORMAT

            # date_from
            date_aux = datetime.strptime(leave.date_from, date_from_date_to_field_type)
            date_aux = self.leaves_context_timestamp(date_aux, request.env.context, request.env.user.tz)
            my_date_from = date_aux.strftime(lang_date_format)

            # date_to
            date_aux = datetime.strptime(leave.date_to, date_from_date_to_field_type)
            date_aux = self.leaves_context_timestamp(date_aux, request.env.context, request.env.user.tz)
            my_date_to = date_aux.strftime(lang_date_format)
        else:
            date_aux = datetime.strptime(fields.Datetime.now(), DEFAULT_SERVER_DATETIME_FORMAT)
            date_aux = self.leaves_context_timestamp(date_aux, request.env.context, request.env.user.tz)
            my_date_from = date_aux.strftime(lang_date_format)
            my_date_to = my_date_from

        values['date_from'] = my_date_from
        values['date_to'] = my_date_to

        return request.render("leaves_management_portal_users.my_leave", values)

    def my_leave_form_validate(self, data, lang):
        '''
        :param data: dictinory of values:
                         'holiday_status_id': int(holiday_status_id) if holiday_status_id else False,
                         'date_from': date_from,
                         'date_to': date_to,
                         'name': name,
        :param lang: res.lang -> language
        :return: erros
        '''
        MANDATORY_BILLING_FIELDS = ["holiday_status_id", "date_from", "date_to"]
        OPTIONAL_BILLING_FIELDS = ["name"]
        error = dict()
        error_message = []
        tz1 = pytz.timezone('UTC')

        date_from = data.get('date_from', None)
        date_from_parsed = None
        if date_from:
            try:
                date_from_parsed = datetime.strptime(date_from, lang.date_format)
                date_from_parsed = self.leaves_context_timestamp(date_from_parsed, request.env.context,
                                                                 request.env.user.tz)
                date_from_parsed = date_from_parsed.replace(hour=0, minute=0, second=0).astimezone(tz1)
            except ValueError:
                error['date_from'] = "not date_from"
                error_message.append(_("Date from should have the following format: '%s'") % (lang.date_format,))
        date_to = data.get('date_to', None)
        date_to_parsed = None
        if date_to:
            try:
                date_to_parsed = datetime.strptime(date_to, lang.date_format)
                date_to_parsed = self.leaves_context_timestamp(date_to_parsed, request.env.context, request.env.user.tz)
                date_to_parsed = date_to_parsed.replace(hour=0, minute=0, second=0).astimezone(tz1)
            except ValueError:
                error['date_to'] = "not date_to"
                error_message.append(_("Date to should have the following format: '%s'") % (lang.date_format,))
        if date_from_parsed and date_to_parsed:
            if date_from_parsed > date_to_parsed:
                error['date_to'] = "wrong date_to"
                error_message.append(_("The start date must be anterior to the end date."))

        # Validation
        for field_name in MANDATORY_BILLING_FIELDS:
            if not data.get(field_name):
                error[field_name] = 'missing'

        # error message for empty required fields
        if [err for err in error.values() if err == 'missing']:
            error_message.append(_('Some required fields are empty.'))

        unknown = [k for k in data.iterkeys() if k not in MANDATORY_BILLING_FIELDS + OPTIONAL_BILLING_FIELDS]
        if unknown:
            unknown_recs_description = request.env['ir.model.fields'].search(
                [('model', '=', 'hr.holidays'), ('name', 'in', unknown)]).mapped('field_description')

            error['common'] = 'Unknown field'
            error_message.append(_("Unknown field '%s'") % ','.join(unknown_recs_description))

        return error, error_message, date_from_parsed, date_to_parsed

    @http.route(['/my/leave/delete/<model("hr.holidays"):leave>',
                 '/my/leave/delete'],
                type='http', auth="user", website=True)
    def delete_leaves(self, leave=None, **kwargs):
        '''
        :param kwargs: ids of the leave to remove
        :return: redirection
        '''
        if not request.env.user or not request.env.user.email:
            return request.render("leaves_management_portal_users.leaves_partner_with_no_mail")
        leaves_to_delete = []
        if leave:
            try:
                leave.unlink()
            except ValidationError as ve:
                request.session['error_unlink'] = ve.name.replace('\n', '')
                request.session['error_unlink_shown'] = False
        else:
            for leave_id in kwargs:
                if leave_id.isdigit() and kwargs[leave_id] == 'on':
                    leaves_to_delete.append(int(leave_id))
            try:
                request.env['hr.holidays'].browse(leaves_to_delete).unlink()
            except Exception as e:
                request.session['error_unlink'] = e.name
                request.session['error_unlink_shown'] = False

        return request.redirect("/my/leaves")
