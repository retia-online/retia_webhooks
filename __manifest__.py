# -*- coding: utf-8 -*-
{
    'name': 'Webhooks',
    'version': '18.0.1.0.0',
    'summary': 'Emisor de Webhooks asíncronos para comunicar Odoo con Next.js/Vercel.',
    'category': 'Technical',
    'author': 'Retia',
    'website': 'https://labs.retia.online',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'crm',
        'project',
    ],
    'data': [
        'views/res_config_settings_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
