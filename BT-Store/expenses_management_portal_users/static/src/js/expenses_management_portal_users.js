
odoo.define('expenses_management_portal_users', function(require) {
    'use strict';
    var core = require('web.core');
    var Model = require('web.Model');
    var _t = core._t;
    var utils = require('web.utils');
    var lang = utils.get_cookie('website_lang') || $('html').attr('lang') || 'en_US';
    lang = lang.substring(0,2);

    $(document).ready(function(){
        var datepicker_date = $('#datepicker-container-date .input-group.date input');
        $('#datepicker-container-date').each(function(){

            datepicker_date.datepicker({
                autoclose: true,
                enableOnReadonly: false,
                todayHighlight: true,
                language: lang,
            });
        });

        var expenses_headers = $('.o_expenses_management_portal_users thead .o_list_record_selector input');
        var expenses_rows = $('.o_expenses_management_portal_users tbody .o_list_record_selector input');
        expenses_rows .prop('checked', false);
        expenses_headers .prop('checked', false);
        expenses_headers.click(function () {
            if (!$(this).prop('checked')) {
                $('#button_to_remove_expenses').addClass('o_hidden');
            } else {
                $('#button_to_remove_expenses').removeClass('o_hidden');
            }
            expenses_rows.prop('checked', $(this).prop('checked') || false);
        });
        expenses_rows.click(function () {
            if (expenses_headers.prop('checked') && !$(this).prop('checked')) {
                expenses_headers.prop('checked', false);
            }
            var something_checked = false;
            var i;
            for (i=0; i<expenses_rows.length; i++) {
                if (expenses_rows[i].checked) {
                    something_checked = true;
                    break;
                }
            }
            if (something_checked) {
                $('#button_to_remove_expenses').removeClass('o_hidden');
            } else {
                $('#button_to_remove_expenses').addClass('o_hidden');
            }
        });
        $('#delete_form').submit(function () {
            if ( ! confirm(_t('Do you really want to remove these records?'))) {
                event.preventDefault();
            }
        });
        $('#delete_expense_id').click(function () {
            if ( ! confirm(_t('Do you really want to remove these records?'))) {
                event.preventDefault();
            } else {
                document.getElementById('to_delete_checkbox').checked = true;
            }
        });
        $('#to_confirm_checkbox').click(function () {
            document.getElementById('to_delete_checkbox').checked = false;
        });
        $('#to_reset_state').click(function () {
            document.getElementById('to_delete_checkbox').checked = false;
        });

        var selection_attachments = $('#select_attachments')[0];
        $('#div_attachments').find("button").click(function () {
            // Remember selected items.
            var is_selected = [];
            var anything_selected = false;
            var selected;
            for (var i = 0; i < selection_attachments.options.length; ++i) {
                selected = selection_attachments.options[i].selected;
                is_selected[i] = selected;
                if (selected) {
                    anything_selected = true;
                }
            }
            if (anything_selected) {
                if (!confirm(_t('Do you really want to remove these attachments?'))) {
                    event.preventDefault();
                } else {
                    // Remove selected items.
                    i = selection_attachments.options.length;
                    while (i--) {
                        if (is_selected[i]) {
                            new Model('ir.attachment').call('unlink', [parseInt(selection_attachments.options[i].value)]);
                            selection_attachments.remove(i);
                        }
                    }
                }
            }
        });

        /*
        code from: https://github.com/odoo/odoo/blob/e653798d5c7e2de957ab35903e54b5998b0418b2/addons/hr_expense/models/hr_expense.py#L74
        @api.onchange('product_id')
        def _onchange_product_id(self):
            if self.product_id:
                if not self.name:
                    self.name = self.product_id.display_name or ''
                self.unit_amount = self.product_id.price_compute('standard_price')[self.product_id.id]
                self.product_uom_id = self.product_id.uom_id
                self.tax_ids = self.product_id.supplier_taxes_id
                account = self.product_id.product_tmpl_id._get_product_accounts()['expense']
                if account:
                    self.account_id = account
        */
        $('.o_expenses_management_portal_users').on('change', "select[name='product_id']", function () {
            var elem = $("select[name='product_id']").find(":selected");
            if (elem.val()) {
                var name = $("input[name='name']");
                if ( !name.val() ) {
                    name.val(elem.text().trim() || '');
                }
                var unit_amount = $("input[name='unit_amount']");
                unit_amount.val(elem.attr('unit_amount') || '1.0');
                var account = elem.attr('account');
                if ( account ) {
                    $("select[name='account_id']").val(account);
                }
            }
        });

    });

});
