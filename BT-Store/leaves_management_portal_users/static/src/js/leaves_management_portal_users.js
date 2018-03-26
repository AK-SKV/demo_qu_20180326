
odoo.define('leaves_management_portal_users', function(require) {
    'use strict';
    var core = require('web.core');
    var _t = core._t;
    var utils = require('web.utils');
    var lang = utils.get_cookie('website_lang') || $('html').attr('lang') || 'en_US';
    lang = lang.substring(0,2);

    $(document).ready(function(){
        var datepicker_date_from_input = $('#datepicker-container-date-from .input-group.date input');
        var datepicker_date_to_input = $('#datepicker-container-date-to .input-group.date input');
        $('#datepicker-container-date-from').each(function(){

            datepicker_date_from_input.datepicker({
                autoclose: true,
                enableOnReadonly: false,
                todayHighlight: true,
                language: lang,
            });
        });
        $('#datepicker-container-date-to').each(function(){

            datepicker_date_to_input.datepicker({
                autoclose: true,
                enableOnReadonly: false,
                todayHighlight: true,
                language: lang,
            });
        });
        datepicker_date_from_input.on("change", function (e) {
            var date_from = datepicker_date_from_input.datepicker("getDate");
            var date_to = datepicker_date_to_input.datepicker("getDate");
            if (date_from > date_to) {
                datepicker_date_to_input.datepicker("setDate", e.currentTarget.value);
            }
            datepicker_date_to_input.datepicker("option", "minDate", date_from);
        });
        datepicker_date_to_input.on("change", function (e) {
            var date_from = datepicker_date_from_input.datepicker("getDate");
            var date_to = datepicker_date_to_input.datepicker("getDate");
            if (date_from > date_to) {
                datepicker_date_from_input.datepicker("setDate", e.currentTarget.value);
            }
            datepicker_date_from_input.datepicker("option", "maxDate", date_to);
        });

        var leaves_headers = $('.o_leaves_management_portal_users thead .o_list_record_selector input');
        var leaves_rows = $('.o_leaves_management_portal_users tbody .o_list_record_selector input');
        leaves_rows .prop('checked', false);
        leaves_headers .prop('checked', false);
        leaves_headers.click(function () {
            if (!$(this).prop('checked')) {
                $('#button_to_remove_leaves').addClass('o_hidden');
            } else {
                $('#button_to_remove_leaves').removeClass('o_hidden');
            }
            leaves_rows.prop('checked', $(this).prop('checked') || false);
        });
        leaves_rows.click(function () {
            if (leaves_headers.prop('checked') && !$(this).prop('checked')) {
                leaves_headers.prop('checked', false);
            }
            var something_checked = false;
            var i;
            for (i=0; i<leaves_rows.length; i++) {
                if (leaves_rows[i].checked) {
                    something_checked = true;
                    break;
                }
            }
            if (something_checked) {
                $('#button_to_remove_leaves').removeClass('o_hidden');
            } else {
                $('#button_to_remove_leaves').addClass('o_hidden');
            }
        });
        $('#delete_form').submit(function () {
            if ( ! confirm(_t('Do you really want to remove these records?'))) {
                event.preventDefault();
            }
        });
        $('#delete_leave_id').click(function () {
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
        $('.o_leaves_management_portal_users').on('change', "select[name='date_from_half_day']", function (e) {
            var select = $("select[name='date_to_half_day']");
            select.val(e.currentTarget.value);
        });
    });

});
