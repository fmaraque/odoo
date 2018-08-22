# -*- encoding: utf-8 -*-
from openerp import fields, models, api

class ResUsers(models.Model):
    _inherit = "res.users"

    is_autor = fields.Boolean(compute='get_moleqla_access', store=True)
    is_editor = fields.Boolean(compute='get_moleqla_access', store=True)
    is_maquetador = fields.Boolean(compute='get_moleqla_access', store=True)
    seccion_editor_ids = fields.Many2many('seccion')
    seccion_maquetador_ids = fields.Many2one('seccion', 'maquetador')

    @api.one
    @api.depends('groups_id')
    def get_moleqla_access(self):
        self.is_autor = self.has_group('moleqla.group_autor')
        self.is_editor = self.has_group('moleqla.group_editor')
        self.is_maquetador = self.has_group('moleqla.group_maquetador')
