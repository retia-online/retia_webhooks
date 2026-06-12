# -*- coding: utf-8 -*-
from odoo import models, api

class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = ['res.partner', 'webhook.dispatcher']

    @api.model_create_multi
    def create(self, vals_list):
        records = super(ResPartner, self).create(vals_list)
        if not self.env.context.get('no_webhook'):
            for record in records:
                self._send_webhook_async('res.partner', 'create', record.id, {
                    'name': record.name,
                    'email': record.email,
                    'phone': record.phone,
                })
        return records

    def write(self, vals):
        res = super(ResPartner, self).write(vals)
        if not self.env.context.get('no_webhook'):
            for record in self:
                # Enviamos sólo los campos modificados en la transacción
                self._send_webhook_async('res.partner', 'write', record.id, vals)
        return res
