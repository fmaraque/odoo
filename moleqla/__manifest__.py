
# -*- encoding: utf-8 -*-
##############################################################################
#
#    Universidad Pablo de Olavide - Sevilla
#
#    
#
#    
#    
#    Módulo diseñado para la Gestión de una revista
#
##############################################################################
{
    "name": "moleqla",
    "version": "1.0",
    "depends": ["base",
                "mail",
                "auth_signup",
                "website"],
    "author": "Author",
    "category": "Moleqla",
    "description": """
       ERP Revista
    """,
    'data': [
                'security/moleqla_security.xml',
                'security/ir.model.access.csv',                
                'views/articulo_graph_view.xml',
                'views/articulo_view.xml',
                'views/seccion_view.xml',                        
                'views/revision_view.xml',
                'views/maquetacion_view.xml',
            ],
    'installable': True,
}