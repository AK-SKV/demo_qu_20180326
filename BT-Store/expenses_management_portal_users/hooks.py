# b-*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2017 brain-tec AG (http://www.braintec-group.com)
# All Right Reserved
#
# See LICENSE file for full licensing details.
##############################################################################

from logging import getLogger
_logger = getLogger(__name__)


def pre_init_hook(cr):
    pass


def post_init_hook(cr, registry):
    _logger.info('Updating ir.rule "res_partner_portal_public_rule" to allow portal users to read other users: '
                 'Needed to submit an expense.')
    cr.execute("""DELETE FROM rule_group_rel WHERE
                  rule_group_id IN (
                      SELECT res_id FROM ir_model_data WHERE name = 'res_partner_portal_public_rule' AND module = 'base'
                  ) AND
                  group_id IN (
                      SELECT res_id FROM ir_model_data WHERE name = 'group_portal' AND module = 'base'
                  );""")


def uninstall_hook(cr, registry):
    cr.execute("""SELECT * FROM rule_group_rel WHERE
                  rule_group_id IN (
                      SELECT res_id FROM ir_model_data WHERE name = 'res_partner_portal_public_rule' AND module = 'base'
                  ) AND
                  group_id IN (
                      SELECT res_id FROM ir_model_data WHERE name = 'group_portal' AND module = 'base'
                  );""")
    r = cr.fetchone()
    if not r:
        cr.execute("SELECT res_id FROM ir_model_data WHERE name = 'group_portal' AND module = 'base';")
        portal = cr.fetchone()[0]
        cr.execute("SELECT res_id FROM ir_model_data WHERE name = 'res_partner_portal_public_rule' AND module = 'base';")
        rule = cr.fetchone()[0]

        _logger.info('Updating ir.rule "res_partner_portal_public_rule" to disallow portal users to read other users: '
                     'As it is by default.')
        cr.execute("""INSERT INTO rule_group_rel (rule_group_id, group_id)
                      VALUES ({0}, {1});""".format(rule, portal))
