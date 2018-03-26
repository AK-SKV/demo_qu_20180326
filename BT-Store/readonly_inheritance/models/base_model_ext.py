# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2017 brain-tec AG (http://www.braintec-group.com)
# All Right Reserved
#
# See LICENSE file for full licensing details.
##############################################################################

from odoo import api, models
from lxml import etree
from ast import literal_eval
from json import dumps


class BaseModelExtend(models.AbstractModel):
    _inherit = 'base'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        def _prepare_dict_string(dict_string):
            return dict_string.replace('true', 'True').replace('false', 'False').replace('null', 'None')

        res = super(BaseModelExtend, self).fields_view_get(view_id=view_id,
                                                           view_type=view_type,
                                                           toolbar=toolbar,
                                                           submenu=submenu)

        doc = etree.XML(res['arch'])
        for node in doc.iter():
            parent = node.getparent()
            # isinstance(node.tag, str) is used to prevent an error if there is a comment in the view definition (e.g. in product.product_template_search_view)
            if isinstance(node.tag, str) and parent is not None:
                parent_modifiers = literal_eval(_prepare_dict_string(parent.get('modifiers', '{}')))

                node_modifiers = literal_eval(_prepare_dict_string(node.get('modifiers', '{}')))
                node_options = literal_eval(_prepare_dict_string(node.get('options', '{}')))

                if parent_modifiers.get('readonly', None) is not None and\
                        not node_options.get('force_this_readonly', None):
                    node_modifiers.update({'readonly': parent_modifiers.get('readonly', None)})

                node.set('modifiers', dumps(node_modifiers))

        res['arch'] = etree.tostring(doc)
        return res
