# -*- coding: utf-8 -*-
import json
import logging
import requests
import threading
from odoo import models, api

_logger = logging.getLogger(__name__)

class WebhookDispatcher(models.AbstractModel):
    _name = 'webhook.dispatcher'
    _description = 'Envío de Webhooks Asíncronos'

    def _send_webhook_async(self, model, event, record_id, vals):
        """Dispara un hilo en segundo plano para realizar el envío HTTP sin bloquear."""
        thread = threading.Thread(
            target=self._send_webhook_request,
            args=(model, event, record_id, vals),
            daemon=True
        )
        thread.start()

    def _send_webhook_request(self, model, event, record_id, vals):
        """Gestiona la petición HTTP POST de manera asíncrona y segura."""
        with api.Environment.manage():
            registry = self.env.registry
            db_name = self.env.cr.dbname
            
            # Crear un cursor dedicado para este hilo independiente
            with registry.cursor() as cr:
                env = api.Environment(cr, self.env.uid, {})
                
                # Obtener parámetros del sistema
                url = env['ir.config_parameter'].sudo().get_param('webhooks.webhook_url')
                secret = env['ir.config_parameter'].sudo().get_param('webhooks.webhook_secret')

                if not url:
                    _logger.warning("Webhooks: URL del Endpoint no configurada.")
                    return

                # Estructura limpia de carga (Payload)
                payload = {
                    'model': model,
                    'event': event,
                    'id': record_id,
                    'vals': vals,
                }

                headers = {
                    'Content-Type': 'application/json',
                }
                if secret:
                    headers['X-Webhook-Secret'] = secret

                try:
                    response = requests.post(url, json=payload, headers=headers, timeout=10)
                    if response.status_code != 200:
                        _logger.error(
                            "Webhooks: Error al enviar webhook (Status %s). Respuesta: %s",
                            response.status_code, response.text
                        )
                except Exception as e:
                    _logger.error("Webhooks: Fallo al conectar con el orquestador: %s", str(e))
