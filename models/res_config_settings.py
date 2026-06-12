# -*- coding: utf-8 -*-
import requests
from odoo import fields, models, api, _
from odoo.exceptions import UserError

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    webhook_url = fields.Char(
        string="Endpoint de Webhooks",
        config_parameter='webhooks_retia.webhook_url',
        help="URL del endpoint externo de Next.js/Vercel (ej. https://tu-orquestador.vercel.app/api/webhooks)"
    )
    webhook_secret = fields.Char(
        string="Secreto de Validación",
        config_parameter='webhooks_retia.webhook_secret',
        help="Token secreto de seguridad que se enviará en la cabecera X-Webhook-Secret o x-odoo-webhook-token"
    )

    def action_test_webhook_connection(self):
        """Envía una petición de prueba al orquestador web y valida su respuesta."""
        self.ensure_one()
        url = self.webhook_url
        secret = self.webhook_secret

        if not url:
            raise UserError(_("Por favor, ingresa el Endpoint de Webhooks antes de realizar la prueba."))

        payload = {
            'event': 'test_connection',
        }
        headers = {
            'Content-Type': 'application/json',
        }
        if secret:
            headers['X-Webhook-Secret'] = secret
            headers['x-odoo-webhook-token'] = secret

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=5)
            if response.status_code == 200:
                try:
                    res_data = response.json()
                    if res_data.get('success'):
                        return {
                            'type': 'ir.actions.client',
                            'tag': 'display_notification',
                            'params': {
                                'title': _('Conexión Exitosa'),
                                'message': res_data.get('message', _('Comunicación activa y autorizada.')),
                                'sticky': False,
                                'type': 'success',
                            }
                        }
                except Exception:
                    pass
                
                # Fallback exitoso si no responde JSON o no tiene success pero es 200
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Conexión Exitosa'),
                        'message': _('El endpoint respondió con código 200 (OK).'),
                        'sticky': False,
                        'type': 'success',
                    }
                }
            elif response.status_code == 401:
                raise UserError(_("No Autorizado (401): El Secreto de Validación no coincide con la configuración del orquestador."))
            elif response.status_code == 404:
                raise UserError(_("No Encontrado (404): La URL ingresada no corresponde al endpoint de webhooks de tu orquestador."))
            else:
                raise UserError(_("Error de Respuesta (%s): El servidor respondió con error. Detalles: %s") % (response.status_code, response.text[:200]))
        except requests.exceptions.RequestException as e:
            raise UserError(_("Fallo de Conexión: No se pudo establecer conexión con el orquestador. Detalles: %s") % str(e))
