=========
Webhooks
=========

Este módulo personalizado de Odoo 18 Community actúa como emisor de Webhooks de salida (Outbound) hacia nuestro orquestador Next.js/Vercel.

Justificación de Modificaciones y Decisiones de Diseño
======================================================

Para integrar este módulo con los logros anteriores (conexión Next.js <=> Odoo) y adaptarlo a producción bajo Docker, hemos realizado los siguientes ajustes:

1. Prevención de Bucles Infinitos (Contexto ``no_webhook``)
----------------------------------------------------------
* **Problema**: Si Next.js actualiza un registro en Odoo a través de la API, y Odoo inmediatamente dispara un webhook de vuelta informando del cambio a Next.js, se generaría un ciclo infinito de peticiones HTTP redundantes.
* **Solución**: Condicionamos la ejecución del dispatcher a que no esté presente el flag ``no_webhook`` en el contexto de Odoo (``self.env.context.get('no_webhook')``). De esta forma, las peticiones entrantes de tu orquestador web pueden realizar cambios en Odoo silenciando la salida del webhook.

2. Gestión de Conexiones Hilo-Seguras (Thread Cursor Management)
----------------------------------------------------------------
* **Problema**: Ejecutar llamadas HTTP asíncronas con ``threading.Thread`` utilizando el cursor activo (``self.env.cr``) puede corromper transacciones o generar errores de base de datos.
* **Solución**: En el dispatcher asíncrono, utilizamos el manejador ``api.Environment.manage()`` y creamos un nuevo cursor con ``with self.env.registry.cursor() as cr:`` para asegurar que el hilo secundario tenga su propia conexión independiente que se cierra limpiamente al finalizar la petición.

3. Compatibilidad con Multi-Creación de Odoo 18 (``@api.model_create_multi``)
-----------------------------------------------------------------------------
* **Problema**: Odoo 18 requiere que el método ``create`` soporte la creación de múltiples registros en un solo lote (``vals_list``).
* **Solución**: Decoramos y estructuramos las sobreescrituras de ``create`` utilizando bucles sobre la lista de registros generados tras invocar a ``super()``.

4. Vistas XML Modernas (Odoo 18 Semantics)
------------------------------------------
* **Problema**: Odoo 17 y 18 utilizan un formato de configuración simplificado basado en las etiquetas ``<app>``, ``<block>`` y ``<setting>``.
* **Solución**: Diseñamos la vista XML de ``res_config_settings_views.xml`` adaptada a esta nueva estructura para garantizar que se renderice limpiamente en la interfaz nativa.

Estructura de Archivos del Módulo
=================================

El módulo se compone de la siguiente estructura modular estándar de Odoo:

::

    webhooks/
    ├── __init__.py
    ├── __manifest__.py
    ├── models/
    │   ├── __init__.py
    │   ├── webhook_dispatcher.py
    │   ├── res_config_settings.py
    │   ├── res_partner.py
    │   ├── crm_lead.py
    │   ├── project_project.py
    │   └── project_task.py
    └── views/
        └── res_config_settings_views.xml

Conclusión de Arquitectura e Integración
========================================

Al utilizar este módulo de Webhooks personalizado, logramos un canal de comunicación bidireccional asíncrona y eficiente entre Odoo y la plataforma web:

1. **Next.js a Odoo (Inbound)**: Resuelto a través de llamadas JSON-RPC/API directa que ya validamos.
2. **Odoo a Next.js (Outbound)**: Resuelto a través de este módulo asíncrono con hilos independientes.
3. **Escalabilidad y Rendimiento**: Dado que el dispatcher realiza llamadas asíncronas, el operador en Odoo no experimenta latencia ni retrasos al crear o guardar registros.
4. **Seguridad**: El token ``X-Webhook-Secret`` garantiza que el endpoint del orquestador Next.js sólo procesará peticiones legítimas firmadas por Odoo.

Plan de Desarrollo del Módulo (Fases y Pasos)
==============================================

El desarrollo del módulo se estructurará en las siguientes etapas clave:

Fase 1: Creación del Módulo en Docker (Entorno Local)
----------------------------------------------------
1. **Crear Estructura**: Crear el directorio ``webhooks`` dentro de la carpeta de addons local mapeada por Docker.
2. **Generar Archivos**: Escribir los manifiestos, archivos ``__init__.py`` y subcarpetas.
3. **Asegurar Permisos**: Validar que los permisos de lectura/escritura de los archivos en el volumen Docker permitan a Odoo cargarlos.

Fase 2: Configuración y Vistas
------------------------------
1. **Crear Modelo de Configuración**: Implementar ``res_config_settings.py`` para almacenar las credenciales de Next.js.
2. **Desplegar Vista**: Incorporar la interfaz XML de configuración en Odoo 18.
3. **Validación Visual**: Reiniciar el contenedor Docker de Odoo, instalar el módulo y verificar que la sección "Webhooks" aparece correctamente en la configuración del sistema.

Fase 3: Lógica del Dispatcher y Modelos Heredados
-------------------------------------------------
1. **Implementar Dispatcher**: Escribir ``webhook_dispatcher.py`` con el método de hilos asíncronos (``threading``).
2. **Agregar Herencia**: Incorporar ``_inherit`` en los modelos de contactos, leads, proyectos y tareas.
3. **Prueba de Log**: Verificar que no ocurran errores de importación de Python al reiniciar Odoo.

Fase 4: Pruebas de Integración y Validación
-------------------------------------------
1. **Configurar Endpoint**: Configurar el webhook en Odoo apuntando a ``http://host.docker.internal:9001/api/webhooks/odoo`` (URL del local server Next.js).
2. **Crear un Lead en Odoo**: Crear o modificar un Lead en Odoo de forma manual y validar en la consola del servidor Next.js que la petición POST del webhook llegó con los datos y el secreto correctos.
3. **Prueba de Prevención de Bucles**: Crear un lead desde Next.js y validar en los logs de Odoo que el webhook de salida NO se disparó (gracias al contexto ``no_webhook``).
