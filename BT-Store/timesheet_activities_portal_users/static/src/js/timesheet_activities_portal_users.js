odoo.define('timesheet_activities_portal_users', function(require) {
    'use strict';
    require('website.website');
    var core = require('web.core');
    var _t = core._t;
    var utils = require('web.utils');
    var lang = utils.get_cookie('website_lang') || $('html').attr('lang') || 'en_US';
    lang = lang.substring(0,2);

    $(function() {
        var o_tapu = $('.o_timesheet_activities_portal_users');
        var o_tapulv = $('.o_timesheet_activities_portal_users_list_view');
        var o_tapu_del_act = $('#o_tapu-delete_activity');

        o_tapulv.find('thead .o_list_record_selector input').prop('checked', false);
        o_tapulv.find('tbody .o_list_record_selector input').prop('checked', false);

        $('#datepicker-container-delivery').each(function(){
            $('#datepicker-container-delivery .input-group.date input').datepicker({
                autoclose: true,
                enableOnReadonly: false,
                todayHighlight: true,
                language: lang,
            });
        });

        var task_options = $("select[name='task_id']:enabled option:not(:first)");
        o_tapu.on('change', "select[name='project_id']", function () {
            var select = $("select[name='task_id']");
            task_options.detach();
            var displayed_state = task_options.filter("[data-project_id="+($(this).val() || 0)+"]");
            var nb = displayed_state.appendTo(select).show().size();
            //select.parent().toggle(nb>=1);
        });

        o_tapu.find("select[name='project_id']").change();

        o_tapulv.find('thead .o_list_record_selector input').click(function () {
            if (!$(this).prop('checked')) {
                o_tapu_del_act.addClass('o_hidden');
            } else {
                o_tapu_del_act.removeClass('o_hidden');
            }
            o_tapulv.find('tbody .o_list_record_selector input').prop('checked', $(this).prop('checked') || false);
        });

        o_tapulv.find('tbody .o_list_record_selector input').click(function () {
            var check_header = o_tapulv.find('thead .o_list_record_selector input');
            if (check_header.prop('checked') && !$(this).prop('checked')) {
                check_header.prop('checked', false);
            }
            var something_checked = false;
            var i;
            var elements = o_tapulv.find('tbody .o_list_record_selector input');
            for (i = 0; i < elements.length; i++) {
                if (elements[i].checked) {
                    something_checked = true;
                    break;
                }
            }
            if (something_checked) {
                o_tapu_del_act.removeClass('o_hidden');
            } else {
                o_tapu_del_act.addClass('o_hidden');
            }
        });

        $('#delete_form').submit(function () {
            if ( ! confirm(_t('Do you really want to remove these records?'))) {
                event.preventDefault();
            }
        });

        $('#delete_timesheet_id').click(function () {
            if ( ! confirm(_t('Do you really want to remove these records?'))) {
                event.preventDefault();
            } else {
                document.getElementById('to_delete_checkbox').checked = true;
            }
        });

        $('#to_confirm_checkbox').click(function () {
            document.getElementById('to_delete_checkbox').checked = false;
        });
    });
});
