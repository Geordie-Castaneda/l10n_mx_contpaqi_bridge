# -*- coding: utf-8 -*-
{
    'name': "l10n_mx_contpaqi_bridge",

    'summary': 'Integración API REST entre Odoo y ContPAQi',
    
    'description': """
        Módulo de integración para sincronización bidireccional entre Odoo y ContPAQi
        
        Funcionalidades principales:
        • Sincronización de Clientes y Proveedores
        • Gestión de Productos y Servicios
        • Control de Inventario y Almacenes
        • Procesos de Compras y Ventas
        • API REST para operaciones CRUD completas
        • Contabilización automática según configuración ContPAQi
        
        Procesos soportados:
        - Creación, actualización y eliminación de documentos
        - Gestión de catálogos (productos, clientes, proveedores)
        - Sincronización de transacciones contables
    """,

    'author': "SISPAV",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/stock_views.xml',
    ]
}
