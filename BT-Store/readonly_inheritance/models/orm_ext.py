# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2017 brain-tec AG (http://www.braintec-group.com)
# All Right Reserved
#
# See LICENSE file for full licensing details.
##############################################################################

from odoo.osv import orm


def simplify_modifiers(modifiers):
    # Don't simplify the 'readonly' element in the modifiers dictionary.
    # To do this, we rename 'readonly' to 'readonly_tmp' and rename it back after processing simplify_modifiers.

    # Otherwise, we don't know if {'readonly': False} is set or if readonly is not set (neither True nor False).
    # If {'readonly': False} ist set, we have to pass this to the sub elements.
    # If readonly is not set, we must not pass anything to the sub elements.

    if 'readonly' in modifiers:
        modifiers['readonly_tmp'] = modifiers.pop('readonly')

    orm.simplify_modifiers_origin(modifiers)

    if 'readonly_tmp' in modifiers:
        modifiers['readonly'] = modifiers.pop('readonly_tmp')


orm.simplify_modifiers_origin = orm.simplify_modifiers
orm.simplify_modifiers = simplify_modifiers
