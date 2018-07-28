# -*- encoding: utf-8 -*-
from openerp import fields, models, api

class seccion(models.Model):
    
    _name = "seccion"
    #_rec_name="display_name"
    _description = "Seccion"
    _inherit = "mail.thread"
    
    name = fields.Char('Nombre', size=128, required=True)
    display_name = fields.Char(compute='get_display_name')
    descripcion = fields.Char('Descripción', size=128)
    max_articulos = fields.Integer('Número máximo de artículos por número', default =3)
    #Only res.users???? Should I need to specify that the group is Editor and Maquetador???
    editor = fields.Many2many('res.users', string='Editor') 
    #editor = fields.Many2many(comodel_name = "res.users",string="Editor",domain=lambda self: [( "groups_id", "=", self.env.ref( "moleqla.editor" ).id )] )

    maquetador = fields.Many2one('res.users', string='Maquetador')
    
    @api.depends('name')
    @api.multi
    def get_display_name(self):
        for record in self:
            record.display_name = record.name
   
seccion()
