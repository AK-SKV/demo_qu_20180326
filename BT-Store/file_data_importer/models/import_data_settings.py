# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2017 brain-tec AG (http://www.braintec-group.com)
#    All Right Reserved
#
#    See LICENSE file for full licensing details.
##############################################################################

from odoo import models, fields, api, _
import csv
import xlrd
import logging

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

_logger = logging.getLogger(__name__)


SUCCESS_IMPORT = _(u'Records have been successfully imported')

FAILED_IMPORT = _(u'There has been a problem while importing the records')

CSV_FORMAT_ERROR = _(u'''Line {row} does not have the right length. It has {col_number} columns instead of 
                    {correct_col_number}''')

XLS_FORMAT_ERROR = _(u'''Line {row} does not have the right length. It has {col_number} columns instead of
                        {correct_col_number}''')

CSV_MISSING_COLUMNS = _(u'The entire field is missing {col_number} columns')

XLS_MISSING_COLUMNS = _(u'The entire field is missing {col_number} columns')


STATUS_SELECTION = [('draft', 'Draft'),
                    ('error', 'Error'),
                    ('success', 'Successful')]

IMPORT_TYPE_SELECTION = [('csv', 'CSV'),
                         ('xls', 'XLS(X)')]


class ImportDataSettings(models.Model):

    _name = 'import.data.settings'

    description = fields.Char('Description')

    import_type = fields.Selection(IMPORT_TYPE_SELECTION)

    import_by = fields.Many2one('res.users',
                                default=lambda self: self.env.user,
                                string='Imported By')

    import_date = fields.Datetime(default=fields.Datetime.now(),
                                  string='Date of the Import')

    content = fields.Binary(string='File')

    content_filename = fields.Char(string='File Name')

    start_row = fields.Integer(string='Starting Row')

    delimiter = fields.Char(string='Delimiter',
                            default=';')

    quotation = fields.Char(string='Quotation',
                            default='"')

    state = fields.Selection(STATUS_SELECTION,
                             default='draft',
                             string='Status')

    total = fields.Integer(string='In Total',
                           compute='_compute_total')

    updated = fields.Integer(string='Updated')

    created = fields.Integer(string='Created')

    object_ids = fields.One2many('import.data.object', 'setting_id',
                                 copy=True,
                                 string='Objects')

    row_limit = fields.Integer(string='Row Limit',
                               help='The rows will be imported in batches of the specified number. '
                                      '-1 means all at once',
                               default=-1)

    total_of_columns = fields.Integer(string='Columns Total', default=-1,
                                      help='Total number of columns of the file. Leave -1 to avoid checking')

    import_data_message_ids = fields.One2many('import.data.message',
                                              'setting_id',
                                              copy=True,
                                              string='Messages')

    @api.multi
    @api.depends('updated', 'created')
    def _compute_total(self):
        for this in self:
            this.total = this.updated + this.created

    def _extract_info_from_csv(self, import_object, start=0, size=False, ignore_lines_with_empty_columns=[], cmp=False):
        """"
        Returns a CSV-parsed iterator of all empty lines in the file

        :throws csv.Error: if an error is detected during CSV parsing
        :throws UnicodeDecodeError: if ``options.encoding`` is incorrect
        Args:
            import_object: object to import. Info from children will be extracted in cascade
            start: row to start extracting the info by
            size: size of batch (number of rows to be read)
            ignore_lines_with_empty_columns: if specified, lines with no info in the indicated columns will be ignored
        """
        error_messages = []
        csv_iterator = csv.reader(StringIO(self.content.decode('base64')),
                                  quotechar=str(self.quotation),
                                  delimiter=str(self.delimiter))
        encoding = 'unicode-escape'

        # Preparing list
        row_list = []
        for row in csv_iterator:
            row_list.append(row)

        # Remove header and already treated rows
        row_list = row_list[start + 1:]

        # Sort if specified a criteria
        if cmp:
            row_list.sort(cmp=cmp)

        # If a size was specified it means that the file will be split and processed in batches
        if size:
            row_list = row_list[0:size]

        # Retrieve the info
        for row_idx, row in enumerate(row_list):
            col_list = [item.decode(encoding) for item in row]

            # The line will be read if it is not empty and has the specified columns
            if col_list and (not ignore_lines_with_empty_columns or
               all(col_list[col_index] for col_index in ignore_lines_with_empty_columns)):
                import_object.extract_csv_info_from_row(list=col_list, row=row_idx)
                error_messages = import_object.get_all_messages()
        return error_messages

    def _extract_info_from_xls(self, env, import_object, start=1, size=False):
        xl_workbook = xlrd.open_workbook(file_contents=self.content.decode('base64'))
        xl_sheet = xl_workbook.sheet_by_index(0)
        nrows = xl_sheet.nrows
        if size <= 0:
            size = nrows

        for row_idx in range(start, min(nrows, start + size)):
            import_object.extract_xls_info_from_row(sheet=xl_sheet, row=row_idx, env=env)
        return import_object.get_all_messages()

    def _check_format_in_csv(self, row_length):
        data = StringIO(self.content.decode('base64'))
        csv_iterator = csv.reader(data,
                                  quotechar=str(self.quotation),
                                  delimiter=str(self.delimiter))
        error_messages = []
        row_idx = self.start_row if self.start_row else 0
        for row in csv_iterator:
            row_idx += 1
            col_list = [item for item in row]
            local_length = len(col_list)
            if local_length != row_length:
                if local_length < row_length:
                    error_messages.append(CSV_MISSING_COLUMNS.format(col_number=row_length-local_length))
                    break
                elif local_length > row_length and col_list[-1]:
                    error_messages.append(CSV_FORMAT_ERROR.format(row=row_idx,
                                                                  col_number=local_length,
                                                                  correct_col_number=row_length))
        return error_messages

    def _check_format_in_xls(self, row_length):
        xl_workbook = xlrd.open_workbook(file_contents=self.content.decode('base64'))
        xl_sheet = xl_workbook.sheet_by_index(0)
        error_messages = []
        local_length = xl_sheet.ncols
        if local_length != row_length:
            if local_length < row_length:
                error_messages.append(XLS_MISSING_COLUMNS.format(col_number=row_length-local_length))
            else:
                starting_row = self.start_row + 1 if self.start_row else 1
                for row_idx in range(starting_row, xl_sheet.nrows):
                    if xl_sheet.cell(row_idx, local_length-1).value:
                        error_messages.append(XLS_FORMAT_ERROR.format(row=row_idx+1,
                                                                      col_number=local_length,
                                                                      correct_col_number=row_length))
        return error_messages

    def _check_format(self, number_of_columns):
        if self.import_type == 'csv':
            return self._check_format_in_csv(number_of_columns)
        return self._check_format_in_xls(number_of_columns)

    def _import(self, import_object, env):
        cr = env.cr
        error_messages = []

        try:
            cr.execute("SAVEPOINT file_data_importer;")
            import_object.import_in_db(env)
            if import_object.check_there_are_errors():
                raise
            cr.execute("RELEASE SAVEPOINT file_data_importer;")
            cr.commit()
            success = not import_object.check_there_are_errors()
        except Exception as e:
            _logger.exception(e)
            success = False
        finally:
            if not success:
                cr.execute("ROLLBACK TO SAVEPOINT file_data_importer;")
                error_messages.insert(0, FAILED_IMPORT)
                error_messages.extend(import_object.get_all_messages())
        return error_messages

    def _get_number_of_rows_from_csv(self):
        csv_iterator = csv.reader(StringIO(self.content.decode('base64')),
                                  quotechar=str(self.quotation),
                                  delimiter=str(self.delimiter))
        return sum(1 for row in csv_iterator)

    def _get_number_of_rows_from_xls(self):
        xl_workbook = xlrd.open_workbook(file_contents=self.content.decode('base64'))
        xl_sheet = xl_workbook.sheet_by_index(0)
        return xl_sheet.nrows

    def _get_number_of_rows(self):
        if self.import_type == 'csv':
            return self._get_number_of_rows_from_csv()
        return self._get_number_of_rows_from_xls()

    def _extract_info(self, env, import_object, start=0, size=False, ignore_lines_with_empty_columns=[], cmp=False):
        error_messages = []

        if self.import_type == 'csv':
            error_messages = self._extract_info_from_csv(env, import_object, start, size)
        else:
            error_messages = self._extract_info_from_xls(env, import_object, start + 1, size)
        return error_messages

    def _extract_info_and_import(self, number_of_columns, import_object):
        '''
        This method wraps the process of extraction of data from the import file and the import to the database.
        It generates batches during the import process if the input file is too long; the user decides to use by filling
         the attribute self.row_limit.
        '''
        env = self.env
        error_messages = []

        # Check file format
        if number_of_columns > 0:
            error_messages = self._check_format(number_of_columns)

        if not error_messages:

            # Extract info
            rows = self._get_number_of_rows()
            windows_size = self.row_limit if self.row_limit > 0 else rows
            starting_row = self.start_row if self.start_row else 0
            for i in range(starting_row, rows, windows_size):
                error_messages.extend(self._extract_info(env, import_object, i, self.row_limit))
                if not error_messages:

                    # Import in db
                    error_messages.extend(self._import(import_object, env))
                    error_messages.extend(import_object.get_all_messages())
                import_object.partial_clear()

        return error_messages

    def _refresh_info(self, import_object, error_messages):
        if not import_object.check_there_are_errors():
            if not error_messages:
                self.set_messages([SUCCESS_IMPORT])
                self.state = 'success'
            else:
                self.set_messages(error_messages)
                self.state = 'error'
        else:
            self.set_messages(error_messages)
            self.state = 'error'
        self.updated = import_object.info_object.updated
        self.created = import_object.info_object.created
        self.import_by = self.env.user
        self.import_date = fields.Datetime.now()

    @api.multi
    def set_messages(self, messages):
        self.ensure_one()
        for x in self.import_data_message_ids:
            x.unlink()
        self.import_data_message_ids = [self.env['import.data.message'].create({'message': x}).id for x in messages]

    @api.multi
    def import_button(self):
        self.ensure_one()
        if self.content:
            for object_id in self.object_ids:

                # Create the import_object to be imported. The child records will be created and linked recursively
                new_import_object = object_id.create_import_object()

                # By importing new_import_object the children are also imported in cascade
                columns_no = self.total_of_columns
                error_messages = self._extract_info_and_import(columns_no, new_import_object)

                # Refresh interface with the results
                self._refresh_info(new_import_object, error_messages)

                # It there were errors the import stops
                if error_messages:
                    break
