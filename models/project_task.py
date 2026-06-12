# -*- coding: utf-8 -*-
from odoo import models, api

class ProjectTask(models.Model):
    _name = 'project.task'
    _inherit = ['project.task', 'webhook.dispatcher']

    @api.model_create_multi
    def create(self, vals_list):
        records = super(ProjectTask, self).create(vals_list)
        if not self.env.context.get('no_webhook'):
            for record in records:
                self._send_webhook_async('project.task', 'create', record.id, {
                    'name': record.name,
                    'project_id': record.project_id.id if record.project_id else False,
                    'stage_id': record.stage_id.id if record.stage_id else False,
                    'description': record.description,
                })
        return records

    def write(self, vals):
        res = super(ProjectTask, self).write(vals)
        if not self.env.context.get('no_webhook'):
            for record in self:
                self._send_webhook_async('project.task', 'write', record.id, vals)
        return res
