# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2017 brain-tec AG (http://www.braintec-group.com)
# All Right Reserved
#
# See LICENSE file for full licensing details.
##############################################################################

from base64 import encodestring
from collections import OrderedDict
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from logging import getLogger

from odoo import fields
from odoo import http, _
from odoo.http import request
from odoo.exceptions import ValidationError

from odoo.addons.website_portal.controllers.main import website_account

_logger = getLogger(__name__)


class WebsiteAccount(website_account):

    @http.route()
    def account(self, **kw):
        response = super(WebsiteAccount, self).account()
        user = request.env.user
        expenses_count = request.env['hr.expense'].sudo().search_count([('employee_id', 'in', user.employee_ids.ids)])
        response.qcontext.update({'expenses': expenses_count})
        return response

    @http.route(['/my/expenses', '/my/expenses/page/<int:page>'],
                type='http', auth="user", website=True)
    def my_expenses(self, page=1, date=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        hr_expenses = request.env['hr.expense']

        sortings = {
            'date': {'label': _('Newest'), 'order': 'date desc'},
            'name': {'label': _('Description'), 'order': 'name'},
        }

        user = values.get('user', 0)
        if user != 0 and user.employee_ids:
            employee_id = user.employee_ids[0].id
        else:
            employee_id = False
        domain = [('employee_id', '=', employee_id)]
        today_date = fields.Datetime.from_string(fields.Datetime.now()).replace(hour=0, minute=0, second=0)
        this_mon = fields.Datetime.to_string(today_date - relativedelta(days=today_date.weekday()))
        this_sun = fields.Datetime.to_string(today_date + relativedelta(days=7 - today_date.weekday() - 1))
        this_month_start = fields.Datetime.to_string(today_date - timedelta(days=today_date.day - 1))
        this_month_end = fields.Datetime.to_string(
            today_date + relativedelta(months=1) - timedelta(days=today_date.day))
        date_filters = {
            'future_expenses': {'label': _('Future expenses'),
                                'domain': [('date', '>=', fields.Datetime.now())]},
            'this_week': {'label': _('This Week'), 'domain': [('date', '>=', this_mon),
                                                              ('date', '<=', this_sun)]},
            'this_month': {'label': _('This Month'), 'domain': [('date', '>=', this_month_start),
                                                                ('date', '<=', this_month_end)]},
            'all': {'label': _('All'), 'domain': []},
        }

        order = sortings.get(sortby, sortings['date'])['order']
        if date_filters.get(date, None):
            domain += date_filters.get(date, None)['domain']
        else:
            domain += date_filters.get('future_expenses')['domain']

        # archive groups - Default Group By 'create_date'
        archive_groups = self._get_archive_groups('hr.expense', domain)
        my_expenses_count = hr_expenses.sudo().search_count(domain)
        values.update({
            'my_expenses_count': my_expenses_count,
        })
        # pager
        pager = request.website.pager(
            url="/my/expenses",
            url_args={'date_from': date, 'sortby': sortby},
            total=values['my_expenses_count'],
            page=page,
            step=self._items_per_page
        )

        # content according to pager and archive selected
        expenses = hr_expenses.sudo().search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])

        values.update({
            'date': date,
            'date_filters': OrderedDict(sorted(date_filters.items())),
            'sortings': sortings,
            'sortby': sortby,
            'expenses': expenses,
            'page_name': 'expense',
            'archive_groups': archive_groups,
            'default_url': '/my/expenses',
            'pager': pager,
            'get_class_state': self.get_class_state,
            'get_description_state': self.get_description_state,
            'translate_func': _,
        })
        if request.session.get('error_unlink', None):
            if request.session.get('error_unlink_shown', None):
                del request.session['error_unlink']
                del request.session['error_unlink_shown']
            else:
                request.session['error_unlink_shown'] = True
        return request.render("expenses_management_portal_users.my_expenses", values)

    def get_description_state(self, state):
        states = request.env['hr.expense']._fields['state']._description_selection(request.env)
        dic_states = {}
        for st in states:
            dic_states[st[0]] = st[1]
        return dic_states.get(state, '')

    def get_class_state(self, state):
        '''
            ('draft', 'To Submit'),
            ('cancel', 'Cancelled'),
            ('confirm', 'To Approve'),
            ('refuse', 'Refused'),
            ('validate1', 'Second Approval'),
            ('validate', 'Approved')
        '''
        css_class = ['label']
        if state == 'draft':
            css_class.append('label-warning')
        elif state == 'reported':
            css_class.append('label-default')
        elif state == 'refused':
            css_class.append('label-danger')
        else:
            css_class.append('label-success')
        return ' '.join(css_class)

    def on_update_error_expenses_portal(self, values, error, error_message, expense_id):
        values.update({
            'error': error,
            'error_message': error_message,
        })
        values.update(self.get_list_of_records())

        if expense_id:
            expense_id = int(expense_id)
            values.update({
                'expense': request.env['hr.expense'].sudo().browse(expense_id),
            })
        return request.render("expenses_management_portal_users.my_expense", values)

    @http.route(['/my/expense/update'],
                type='http', auth="public", methods=['POST'], website=True, csrf=False)
    def expense_update(self, expense_id, name, product_id, reference, unit_amount, date, quantity, account_id,
                       payment_mode, description, attachment,
                       to_delete=False, **kw):
        if to_delete:
            return request.redirect("/my/expense/delete/%s" % (expense_id,))
        lang = request.env['res.lang'].search([('code', 'like', request.httprequest.cookies.get('website_lang'))],
                                              limit=1)
        values = {
            'product_id': int(product_id) if product_id else False,
            'date': date,
            'name': name,
            'reference': reference,
            'unit_amount': unit_amount,
            'quantity': quantity,
            'account_id': int(account_id) if account_id else False,
            'payment_mode': payment_mode,
            'description': description,
        }
        error, error_message, date_parsed = self.my_expense_form_validate(values, lang)
        values.update({
            'date_format': lang.date_format.replace('%m', 'mm').replace('%d', 'dd').replace('%Y', 'yyyy'),
        })
        if not error:
            vals_to_write = dict(values)
            if 'date_format' in vals_to_write:
                del vals_to_write['date_format']
            if date_parsed is not None:
                values.update({
                    'date': date_parsed.strftime(lang.date_format),
                })
                vals_to_write.update({
                    'date': fields.Date.to_string(date_parsed),
                })
            if expense_id:
                expense_id = int(expense_id)

                try:
                    request.env['hr.expense'].browse(expense_id).write(vals_to_write)
                    if attachment:
                        attachment_value = {
                            'name': '{0} {1} - {2}'.format(_('Expense'), name, attachment.filename),
                            'datas': encodestring(attachment.read()),
                            'datas_fname': attachment.filename,
                            'res_model': 'hr.expense',
                            'res_id': expense_id,
                        }
                        request.env['ir.attachment'].sudo().create(attachment_value)
                except ValidationError as ve:
                    error['general'] = "Validation error"
                    error_message.append(ve.name)
                    return self.on_update_error_expenses_portal(values, error, error_message, expense_id)
            else:
                user = request.env.user
                if not user.employee_ids:
                    error['employee_id'] = "not employee_id set"
                    error_message.append(_("Please make sure that your user has an employee assigned "
                                           "(contact with the administrator)."))
                    return self.on_update_error_expenses_portal(values, error, error_message, expense_id)
                if not user.partner_id or not user.partner_id.email:
                    error['partner_id'] = "not partner_id set"
                    error_message.append(_("Please make sure that your user has a partner assigned with an email "
                                           "(contact with the administrator, or modify your data on the section "
                                           "'Your Details')."))
                    return self.on_update_error_expenses_portal(values, error, error_message, expense_id)

                vals_to_write.update({
                    'employee_id': user.employee_ids[0].id,
                })
                try:
                    new_expense = request.env['hr.expense'].create(vals_to_write)
                    if attachment:
                        attachment_value = {
                            'name': '{0} {1} - {2}'.format(_('Expense'), name, attachment.filename),
                            'datas': encodestring(attachment.read()),
                            'datas_fname': attachment.filename,
                            'res_model': 'hr.expense',
                            'res_id': new_expense.id,
                        }
                        request.env['ir.attachment'].sudo().create(attachment_value)
                except ValidationError as ve:
                    error['general'] = "Validation error"
                    error_message.append(ve.name)
                    return self.on_update_error_expenses_portal(values, error, error_message, expense_id)
            return request.redirect("/my/expenses")
        else:
            return self.on_update_error_expenses_portal(values, error, error_message, expense_id)

    def get_list_of_records(self):
        product_ids = request.env['product.product'].search([('can_be_expensed', '=', True)])
        accounts = request.env['account.account'].search([])
        return {
            'product_ids': product_ids,
            'accounts': accounts,
        }

    @http.route(['/my/expense/<model("hr.expense"):expense>',
                 '/my/expense/create'],
                type='http', auth="user", website=True)
    def my_expense(self, expense=None, **kwargs):

        values = {
            'error': {},
            'error_message': [],
        }

        lang = request.env['res.lang'].search([('code', 'like', request.httprequest.cookies.get('website_lang'))],
                                              limit=1)
        default_account = request.env['ir.property'].get('property_account_expense_categ_id', 'product.category')

        values.update({
            'expense': expense,
            'date': fields.Date.from_string(
                expense.date).strftime(lang.date_format) if expense else fields.Date.from_string(
                fields.Date.today()).strftime(lang.date_format),
            'account_id': default_account.id if default_account else False,
        })
        values.update(self.get_list_of_records())

        if expense and expense.attachment_number:
            attachments = request.env['ir.attachment'].search(
                [('res_model', '=', 'hr.expense'), ('res_id', 'in', expense.ids)])
            values.update({
                'attachments': attachments.name_get()
            })

        return request.render("expenses_management_portal_users.my_expense", values)

    def get_mandatory_billing_fields(self):
        return ["name", "product_id", "quantity", "payment_mode"]

    def get_optional_billing_fields(self):
        return ["reference", "unit_amount", "date", "account_id", "description"]

    def my_expense_form_validate(self, data, lang):
        '''
        :param data: dictinory of values:
                         'holiday_status_id': int(holiday_status_id) if holiday_status_id else False,
                         'date_from': date_from,
                         'date_to': date_to,
                         'name': name,
        :param lang: res.lang -> language
        :return: erros
        '''
        MANDATORY_BILLING_FIELDS = self.get_mandatory_billing_fields()
        OPTIONAL_BILLING_FIELDS = self.get_optional_billing_fields()
        error = dict()
        error_message = []

        date = data.get('date', None)
        date_parsed = None
        if date:
            try:
                date_parsed = datetime.strptime(date, lang.date_format).date()
            except ValueError:
                error['date_from'] = "not date_from"
                error_message.append(_("Date from should have the following format: '%s'") % (lang.date_format,))

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
                [('model', '=', 'hr.expense'), ('name', 'in', unknown)]).mapped('field_description')

            error['common'] = 'Unknown field'
            error_message.append(_("Unknown field '%s'") % ','.join(unknown_recs_description))

        return error, error_message, date_parsed

    @http.route(['/my/expense/delete/<model("hr.expense"):expense>',
                 '/my/expense/delete'],
                type='http', auth="user", website=True)
    def delete_expenses(self, expense=None, **kwargs):
        '''
        :param expense: expense to inspect
        :param kwargs: ids of the leave to remove
        :return: redirection
        '''
        expenses_to_delete = []
        if expense:
            try:
                expense.unlink()
            except ValidationError as ve:
                request.session['error_unlink'] = ve.name.replace('\n', '')
                request.session['error_unlink_shown'] = False
        else:
            for expense_id in kwargs:
                if expense_id.isdigit() and kwargs[expense_id] == 'on':
                    expenses_to_delete.append(int(expense_id))
            try:
                request.env['hr.expense'].browse(expenses_to_delete).unlink()
            except Exception as e:
                request.session['error_unlink'] = e.name
                request.session['error_unlink_shown'] = False

        return request.redirect("/my/expenses")

    @http.route(['/my/expense/submit/<model("hr.expense"):expense>'],
                type='http', auth="user", website=True)
    def submit_expense(self, expense, **kwargs):
        '''
        :param expense: expense to submit
        :param kwargs:
        :return: redirection
        '''
        if expense:
            if not expense.sheet_id:
                # The following function cannot be used because it does not submit the expense directly:
                # It returns an action, with a new object expected to be saved manually, i.e.,
                # it cannot be used in the website
                # expense.submit_expenses()

                # Creating the expense.sheet manually
                request.env['hr.expense.sheet'].create({
                    'expense_line_ids': [(4, expense.id, False)],
                    'employee_id': expense.employee_id.id,
                    'name': expense.name,
                })
            else:
                expense.sheet_id.reset_expense_sheets()

        return request.redirect("/my/expenses")
