# -*- encoding: utf-8 -*-
from openerp import fields, models, api

class seccion(models.Model):
    
    _name = "seccion"
    _description = "Seccion"
    _inherit = "mail.thread"
    
    nombre = fields.Char('Nombre', size=128)
    display_name = fields.Char(compute='get_display_name')
    descripcion = fields.Char('Descripción', size=128)
    max_articulos = fields.Integer('Número máximo de artículos por número', default =3)
    editor = fields.One2many('editor', 'seccion_id','Editor') 
    maquetador = fields.One2many('maquetador', 'seccion_id','Maquetador')
    
    @api.depends('nombre')
    @api.multi
    def get_display_name(self):
        for record in self:
            record.display_name = record.nombre
   
seccion()