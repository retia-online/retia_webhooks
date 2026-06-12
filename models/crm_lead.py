# -*- coding: utf-8 -*-
from odoo import models, api

class CrmLead(models.Model):
    _name = 'crm.lead'
    _inherit = ['crm.lead', 'webhook.dispatcher']

    @api.model_create_multi
    def create(self, vals_list):
        records = super(CrmLead, self).create(vals_list)
        if not self.env.context.get('no_webhook'):
            for record in records:
                self._send_webhook_async('crm.lead', 'create', record.id, {
                    'name': record.name,
                    'partner_id': record.partner_id.id if record.partner_id else False,
                    'stage_id': record.stage_id.id if record.stage_id else False,
                    'description': record.description,
                })
        return records

    def write(self, vals):
        res = super(CrmLead, self).write(vals)
        if not self.env.context.get('no_webhook'):
            for record in self:
                self._send_webhook_async('crm.lead', 'write', record.id, vals)
        return res
