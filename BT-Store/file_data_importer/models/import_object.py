# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2017 brain-tec AG (http://www.braintec-group.com)
#    All Right Reserved
#
#    See LICENSE file for full licensing details.
##############################################################################

from odoo import fields, _, SUPERUSER_ID
from collections import OrderedDict
from copy import copy
import re
import logging
_logger = logging.getLogger(__name__)

EXCEPT_READING_FILE = _(u'Checking needed on row {row_number} and column {column_number}, data has an unknown format. '
                        u'Error: {error}')

EXCEPT_COMPUTING_KEY = _(u'Error while computing the key for model {model_name} in line {row_number}. '
                         u'Error: {error}')

EXCEPT_UPDATING = _(u'Error while updating the record identified by {keys} as {identifier}. Reason: {error}')

EXCEPT_CREATING = _(u'Error while creating the record identified by {keys} as {identifier}. Reason: {error}')

EXCEPT_PARTNER_NOT_FOUND = _(u'The partner with name {0} has not been found in the system')

EXCEPT_LINKING = _(u'Error while linking records: {0}')

COST_CENTER = _(u'Cost Center')

INCOMPLETE_KEY_DEFINITION = _(u'The column {col} to be treated as key is not fully defined or no content was found in '
                              u'their columns')


def has_invoice_number_format(value):
    match = re.match('(ER|ZA|ZF)\d{8}', value)
    return True if match else False


def has_contra_account_format(value):
    return len(value) == 8


def extract_value_from_xls_sheet(kwargs):
    xl_sheet = kwargs['sheet']
    row_idx = kwargs['row']
    col_idx = kwargs['col']
    return xl_sheet.cell(row_idx, col_idx).value


def extract_value_from_csv_row(kwargs):
    row = kwargs['list']
    col_idx = kwargs['col']
    return row[col_idx]


class InfoObject:
    '''
    Defines an object which contains the relevant info to be retrieved during the process of import.
    '''
    def __init__(self):
        self.updated = 0
        self.created = 0
        self.messages = []
        self.errors = False


class ImportObject:
    '''
    Defines an object which contains the logical concept extracted from a file.

    Attributes:
        @ivar columns                      Dictionary. Key: its number in the file and Value: the name given to the column
        @ivar types                        Dictionary. Key the name of the column and Value: its python type.
        @ivar defaults                     Dictionary. Key the name of the column and Value: its python type.
        @ivar apply_defaults               Dictionary. Key the name of the column and Value: True if the column is
                                           requested to be applyed only when creating record. False if it is requested
                                           to be applied in both create and update
        @ivar model                        String containing the name of the odoo model asociated.
        @ivar keys                         List of strings. Each string is the name of a column that matches the name of
                                           the column in the database.
                                           All the elements in the list together make the object unique.
        @ivar key_function                 Transforms the keys into a single key identifier.
                                           For example, it is needed when an object is identified by several columns;
                                           this function allows the object be hashable by a single value.
        @ivar _objects_dict                Dictionary. Key: the key generated by key_function and Value: Dictionnary:
                                           Key: name of column and Value: value of the column.
        @ivar related_objects              List of import_objects contained in the current object.
                                           For example, a parcel may contain district, municipality, owners, etc.
        @ivar parent_import_object         import_object that contains the current object.
        @ivar parent_field                 If it is specified it represents the odoo name of the field in the parent
                                           that will contain the current objects as children. For example, owner_ids.
        @ivar m2o_field                    It is the name of the field that points to the parent (the one2many object).
                                           It is only being used in case that the object to import is the "many" object
                                           in the relation.
        @ivar _parent_children_rel_dict    If it specified it is a dictionary where Key: key generated by key_function
                                           that represents the parent object and Value: list containing keys generated
                                           by key_function representing the child objects.
        @ivar _last_read_key               Key generated by key_function that stores the last read row.
        @ivar _object_ids_dict             Dictionary where Key: key generated by key_function and Value: record
                                           corresponding to that value.
        @ivar info_object                  Contains the relevant info during the import process.
        @ivar import_date:                 Date of the import.
        @ivar is_to_be_used_as_key:        This indicates that, when searching for a record given its keys, the children
                                           with this flag True indicates that it is to be added as key as well. It is
                                           useful when checking the existence of one2many records and it is needed to
                                           check the parent_id.
    '''

    def __init__(self,
                 columns,
                 types,
                 defaults,
                 column_apply_defaults,
                 model,
                 keys,
                 key_function,
                 parent_import_object=None,
                 parent_field=None,
                 m2o_field=None,
                 is_to_be_used_as_key=False):
        self.columns = columns
        self.types = types
        self.column_defaults = defaults
        self.column_apply_defaults = column_apply_defaults
        self.model = model
        self.keys = keys
        self.key_function = key_function
        self._objects_dict = OrderedDict()
        self.related_objects = []
        self.parent_import_object = parent_import_object
        if parent_import_object is not None:
            parent_import_object.related_objects.append(self)
        self.parent_field = parent_field
        self.m2o_field = m2o_field
        self._parent_children_rel_dict = {}
        self._last_read_key = None
        self._object_ids_dict = {}
        self.info_object = InfoObject()
        self.import_date = fields.Datetime.now()
        self.is_to_be_used_as_key = is_to_be_used_as_key

    def _partial_clear(self):
        '''
        This methods clears the specified object but not the info related to the objects it will import
        (columns, types, keys...) to allow keep importing new info.
        '''
        self._objects_dict = OrderedDict()
        self._parent_children_rel_dict = {}
        self._last_read_key = None
        self._object_ids_dict = {}


    def partial_clear(self):
        '''
        This method clears the objects extracted but not the info related to them (columns, types, keys...) to allow
        keep importing new info.
        '''
        for import_object in self.related_objects:
            import_object.partial_clear()
        self._partial_clear()

    def _set_extra_values(self, env, values):
        new_values = copy(values)
        return new_values

    def extract_key_from_children(self, env, key, function, kwargs):
        """
        Extracts value from the related objects. Precisely, it iterates throught all the related objects (children)
        looking for the one whose related field is called as key. Then it prefetches its id and it is returned.
        """
        domain = []
        for obj in self.related_objects:
            if obj.is_to_be_used_as_key and obj.parent_field == key:
                for key in obj.keys:
                    col = [k for k in obj.columns if obj.columns.get(k) == key][0]
                    kwargs['col'] = col
                    value = obj.types[key](function(kwargs))
                    if value:
                        domain.append((key, '=', value))
                records = env[obj.model].search(domain)
                return records.ids[0] if records else False
        return False

    def extract_xls_info_from_row(self, **kwargs):
        self._extract_info_from_row(function=extract_value_from_xls_sheet, kwargs=kwargs)

    def extract_csv_info_from_row(self, **kwargs):
        self._extract_info_from_row(function=extract_value_from_csv_row, kwargs=kwargs)

    def keys_coming_from_children(self, key):
        as_key_fields = [x.parent_field for x in self.related_objects if x.is_to_be_used_as_key]
        return key in as_key_fields

    def _extract_info_from_row(self, function, kwargs):
        env = kwargs.get('env')
        row_idx = kwargs.get('row')

        local_dict = dict()

        # Prefetch values that come from "as key" child objects
        for key in filter(self.keys_coming_from_children, self.keys): # For the keys that are not in columns
            value = self.extract_key_from_children(env, key, function, kwargs)
            if value:
                local_dict[key] = value
            else:
                if key in local_dict:
                    del local_dict[key]

                # Workaround to force creation later on
                local_dict['id'] = 0

                break

        # Simple fields
        for col_idx, col_name in self.columns.items():
            kwargs['col'] = col_idx
            try:
                value = self.types[col_name](function(kwargs))

                # If the key was already inserted it will be replaced if the new value is not empty
                # or if the key was not inserted, obviously.
                if col_name in local_dict and value or col_name not in local_dict:
                    local_dict[col_name] = value
                elif not value:

                    # If the cell contains no value the defaults are checked
                    default_value = self.column_defaults.get(col_name, False)
                    if default_value:
                        local_dict[col_name] = default_value
            except Exception as e:
                self.info_object.messages.append(EXCEPT_READING_FILE.format(row_number=row_idx,
                                                                            column_number=col_idx,
                                                                            error=e))

        # Apply the defaults in case some missing keys are contained there
        for key, value in self.column_defaults.iteritems():
            if key not in local_dict:
                local_dict[key] = value

        # local_dict must contain some value from the row and, at least,
        # the values of the keys that identify the object
        can_continue = all(key in local_dict for key in self.keys)

        if local_dict and can_continue:
            # adding the extracted object to the existing ones
            try:
                self._last_read_key = self.key_function(local_dict, self.keys)
            except Exception as e:
                self.info_object.messages.append(EXCEPT_COMPUTING_KEY.format(model_name=self.model,
                                                                             row_number=row_idx,
                                                                             error=e))
            type_of_key = type(self._last_read_key)
            if (self._last_read_key and
               len(self._last_read_key) > 0 if type_of_key not in  (int, float) else self._last_read_key > 0 or
               self.model == 'account.analytic.account' and self._last_read_key == 0):
                if self._last_read_key not in self._objects_dict:
                    self._objects_dict[self._last_read_key] = local_dict

                # linking to the parent
                if self.parent_import_object:
                    if self.parent_import_object._last_read_key not in self._parent_children_rel_dict:
                        self._parent_children_rel_dict[self.parent_import_object._last_read_key] = [self._last_read_key]
                    elif self._last_read_key not in self._parent_children_rel_dict[self.parent_import_object._last_read_key]:
                            self._parent_children_rel_dict[self.parent_import_object._last_read_key].append(self._last_read_key)

        # extracting info for the related objects
        for r in self.related_objects:
            r._extract_info_from_row(function, kwargs)

    def _update_in_db(self, record, values):
        # As it is right now, all values from the record are being updated.
        # Another approach may consist in update just the different values and, if there is none,
        # consider the record as untouched
        # For some reason res.country is low performant when being updated and it's never goint to be really necessary
        # The invoices themselves are never updated (only the objects they are related to)
        if self.model not in ('res.country',):
            record.write(values)

    def _create_in_db(self, env, values):
        record = env[self.model].create(values)
        return record

    def _apply_default_values(self, mode, local_dict):

        # Default values
        for col_name, default_value in self.column_defaults.items():
            if col_name not in local_dict:
                if mode == 'creating' or mode == 'updating' and not self.column_apply_defaults[col_name]:
                    local_dict[col_name] = default_value

    def import_in_db(self, env):
        success = True

        # updating and creating the objects
        for (key, values) in self._objects_dict.iteritems():
            updated_values = self._set_extra_values(env, values)
            keys_domain = [(x, '=', values.get(x)) for x in self.keys]
            # cost centers can be inactive, so these must be considered too
            if self.model == 'account.analytic.account':
                keys_domain.extend([
                    '|',
                    ('active', '=', True),
                    ('active', '=', False),
                ])
            records = env[self.model].search(keys_domain)
            if len(records) > 0:
                record = records[0]
                try:

                    # Apply default values if requested
                    self._apply_default_values('updating', updated_values)

                    self._update_in_db(record, updated_values)
                    self.info_object.updated += 1
                    success = True
                except Exception as e:
                    _logger.error(e)
                    self.info_object.messages.append(EXCEPT_UPDATING.format(keys=self.keys,
                                                                            identifier=self.key_function(values,
                                                                                                         self.keys),
                                                                            error=e))
                    success = False
            else:
                try:

                    # Apply default values if requested
                    self._apply_default_values('creating', updated_values)

                    record = self._create_in_db(env, updated_values)
                    self.info_object.created += 1
                    success = True
                except Exception as e:
                    _logger.error(e)
                    self.info_object.messages.append(EXCEPT_CREATING.format(keys=self.keys,
                                                                            identifier=self.key_function(values,
                                                                                                         self.keys),
                                                                            error=e))
                    success = False
            if success:
                self._object_ids_dict[key] = record
            else:
                # the cursor wont make rollback because of a faulty res.partner, as requested by Dominik
                self.info_object.errors = True and self.model != 'res.partner'
        # updating and creating the relations
        try:
            for key, values in self._parent_children_rel_dict.iteritems():
                # if the parent could be created (has a record associated)
                if key in self.parent_import_object._object_ids_dict:
                    children = [self._object_ids_dict[x] for x in values if x in self._object_ids_dict]
                    # if there are children (maybe the relationship exists but there is no record: account.invoice)
                    if children:
                        parent_record = self.parent_import_object._object_ids_dict[key]
                        ir_model_fields = env['ir.model.fields'].search([('model', '=', self.parent_import_object.model),
                                                                         ('name', '=', self.parent_field)])
                        parent_fild_type = ir_model_fields[0].ttype
                        if parent_fild_type == 'one2many':
                            for child in children:
                                setattr(child, self.m2o_field, parent_record)
                        else:
                            children_ids = [x.id for x in children]
                            if parent_fild_type == 'many2many':
                                setattr(parent_record, self.parent_field, children_ids)
                            elif parent_fild_type == 'many2one':
                                setattr(parent_record, self.parent_field, children_ids[0])
        except Exception as e:
            self.info_object.messages.append(EXCEPT_LINKING.format(e))

        # importing related objects
        for r in self.related_objects:
            r.import_in_db(env)

    def get_all_messages(self):
        messages = []

        def _get_messages(import_object, messages):
            messages.extend(import_object.info_object.messages)
            for x in import_object.related_objects:
                _get_messages(x, messages)

        _get_messages(self, messages)
        return messages

    def check_there_are_errors(self):

        def _get_there_is_some_error(import_object):
            there_is = import_object.info_object.errors
            for x in import_object.related_objects:
                there_is = there_is or _get_there_is_some_error(x)
            return there_is

        return _get_there_is_some_error(self)

    def get_records(self):
        return self._object_ids_dict.values()

    def _get_ids_for_one2many_field(self, pool, cr, uid, parent_record, children_ids, _parent_children_rel_dict):
        '''
        This function is not used. It has been made to be used when linking records to a one2many field.
        Since an id can not be linked to more than one parent, it checks whether an id is already taken by another
        record (the many2one record). If so, it creates a copy of it to be assigned to the local record.
        It returns the list of ids, created and already existing (if they were not taken by any parent) so you can
        assign this list of ids directly.
        '''
        refined_ids_list = []
        for id in children_ids:
            found = False
            for parent in _parent_children_rel_dict.keys():
                parent_record_aux = self.parent_import_object._object_ids_dict[parent]
                if (parent_record.id != parent_record_aux.id and
                id in [x.id for x in getattr(parent_record_aux, self.parent_field)]):
                    found = True
                    break
            if found:
                copy = pool[self.model].browse(cr, uid, id).copy()
                refined_ids_list.append(copy)
            else:
                refined_ids_list.append(id)
        return refined_ids_list
