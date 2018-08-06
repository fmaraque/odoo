# -*- encoding: utf-8 -*-
from openerp import fields, models, api

class seccion(models.Model):
    
    _name = "seccion"
    _description = "Seccion"
    _inherit = "mail.thread"
    
    name = fields.Char('Nombre', size=128, required=True)
    descripcion = fields.Char('Descripción', size=128)
    max_articulos = fields.Integer('Número máximo de artículos por número', default =3)
    editor_ids = fields.Many2many('res.users', string='Editors', domain="[('is_editor', '=', True)]")
    maquetador = fields.Many2one('res.users', string='Maquetador', domain="[('is_maquetador', '=', True)]")