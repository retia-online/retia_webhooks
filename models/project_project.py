# -*- coding: utf-8 -*-
from odoo import models, api

class ProjectProject(models.Model):
    _name = 'project.project'
    _inherit = ['project.project', 'webhook.dispatcher']

    @api.model_create_multi
    def create(self, vals_list):
        records = super(ProjectProject, self).create(vals_list)
        if not self.env.context.get('no_webhook'):
            for record in records:
                self._send_webhook_async('project.project', 'create', record.id, {
                    'name': record.name,
                })
        return records

    def write(self, vals):
        res = super(ProjectProject, self).write(vals)
        if not self.env.context.get('no_webhook'):
            for record in self:
                self._send_webhook_async('project.project', 'write', record.id, vals)
        return res
