# -*- encoding: utf-8 -*-
from openerp import fields, models, api

class seccion(models.Model):
    
    _name = "seccion"
    _description = "Seccion"
    
    
    nombre = fields.Char('Nombreeeeee', size=128)
    descripcion = fields.Char('Descripción', size=128)
    max_articulos = fields.Integer('Número máximo de artículos por número', default =3)
    editor = fields.One2many('editor', 'seccion_id','Editor') 
    maquetador = fields.One2many('maquetador', 'seccion_id','Maquetador')
    
    
   
seccion()