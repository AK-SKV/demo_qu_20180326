# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2017 brain-tec AG (http://www.braintec-group.com)
# All Right Reserved
#
# See LICENSE file for full licensing details.
##############################################################################

from odoo import api, fields, models


class ProjectTaskExt(models.Model):
    _inherit = 'project.task'

    parent_id = fields.Many2one(comodel_name='project.task', string='Parent Task')
    child_ids = fields.One2many(comodel_name='project.task', inverse_name='parent_id',
                                string='Child tasks')
    subtask_count = fields.Integer('Sub-tasks', compute='_compute_subtask_count')

    @api.multi
    def _compute_subtask_count(self):
        """
        Required for the kanban view
        """
        for project_task in self:
            project_task.subtask_count = len(project_task.child_ids)

    @api.model
    def create(self, vals):
        if 'parent_id' in vals:
            parent = self.browse(vals['parent_id'])
            if parent.project_id:
                vals['project_id'] = parent.project_id.id
            if parent.stage_id:
                vals['stage_id'] = parent.stage_id.id
        return super(ProjectTaskExt, self).create(vals)

    @api.multi
    def write(self, vals):
        """
        Propagates a change of stage in every circumstance.
            E.g.: a faulty onchange declaration
        """
        if 'project_id' in vals:
            # it is not possible to use onchange in this case so far:
            # https://github.com/odoo/odoo/issues/2693
            for project_task in self:
                if project_task.child_ids:
                    project_task.child_ids.write({'project_id': vals['project_id']})
        ret = super(ProjectTaskExt, self).write(vals)
        if 'stage_id' in vals:
            self.onchange_state()
        return ret

    @api.onchange('stage_id')
    def onchange_state(self):
        """
        Any no-archived subtask will have the same stage as
            its parent on a change of the parent stage
        """
        for project_task in self:
            if project_task.active:
                for child in project_task.child_ids:
                    if child.active and child.stage_id.id != project_task.stage_id.id:
                        child.stage_id = project_task.stage_id.id

    @api.multi
    def open_subtasks(self):
        self.ensure_one()
        ctx = self._context.copy()
        ctx.update({
            'search_default_parent_id': [self.id],
            'default_parent_id': self.id,
            'search_default_project_id': self.project_id.id,
            'default_project_id': self.project_id.id,
            'search_default_noparentid': 0,
        })
        return {
            'name': self.name,
            'type': 'ir.actions.act_window',
            'view_type': 'tree',
            'view_mode': 'kanban,tree,form,calendar,pivot,graph',
            'res_model': 'project.task',
            'context': ctx,
        }
