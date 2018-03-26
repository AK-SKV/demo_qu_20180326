odoo.define('shift_multiple_select', function (require) {
      "use strict";
      var ListView = require('web.ListView');
      ListView.List = ListView.List.extend({

            // We just override delegate for record selector in the init function of ListView.List object
            // so that all the checkboxes between a couple of checkboxes already selected are checked automatically
            init: function () {

                var self = this;
                var result = this._super.apply(this, arguments);
                this.lastChecked = null;

                this.$current = $('<tbody>')
                    .delegate('td.o_list_record_selector', 'click', function (e) {
                        e.stopPropagation();

                        /////////////////////////////////////////////////////////////////////
                        // New code
                        var thisChkBox = $(this).find("input").get(0)

                        if (self.lastChecked && e.shiftKey) {
                            var $chkboxes = self.$current.find('td.o_list_record_selector input')
                            var start = $chkboxes.index(thisChkBox);
                            var end = $chkboxes.index(self.lastChecked);
                            $chkboxes.slice(Math.min(start, end), Math.max(start, end) + 1).prop('checked', self.lastChecked.checked);
                        }
                        self.lastChecked = thisChkBox
                        /////////////////////////////////////////////////////////////////////

                        var selection = self.get_selection();
                        var checked = $(e.currentTarget).find('input').prop('checked');
                        $(self).trigger(
                            'selected', [selection.ids, selection.records, ! checked]);
                    })
                    return result;
                },
        });
})

