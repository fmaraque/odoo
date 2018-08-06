# -*- encoding: utf-8 -*-
from openerp import fields, models, api
from openerp.osv import osv

class maquetacion(models.Model):
    
    _name = "maquetacion"
    _description = "Maquetacion"
    _inherit = "mail.thread"
          
    articulo_id = fields.Many2one('articulo', 'Articulo')
    seccion_id = fields.Many2one('seccion', 'Sección')
    observaciones = fields.Binary('Observaciones')
    filenameObv = fields.Char('FilenameObv', default='observaciones.pdf')
    
    maquetador_id = fields.Many2one('res.users','Maquetador', domain="[('is_maquetador', '=', True)]")
    state = fields.Selection([('start', 'En Maquetación'), ('send', 'Maquetado'), ('cancel', 'Rechazado')], 'Estado de la maquetación', default='start')
    comentarios = fields.Text('Comentarios')
    versiones_anteriores = fields.One2many('articulo', 'old_maquetacion_id', 'Versiones anteriores')
    articulo_nombre = fields.Char(related='articulo_id.name', string='Nombre', readonly=True)
    display_name = fields.Char(compute='get_display_name')
    articulo_descripcion = fields.Text(related='articulo_id.descripcion', string='Descripción', readonly=True)
    articulo_seccion = fields.Many2one(related='articulo_id.seccion_id', string='Sección', comodel_name='seccion', readonly=True)
    articulo_tipoArticulo = fields.Selection(related='articulo_id.tipo_articulo', string='Tipo Artículo', readonly=True)
    articulo_tipoAutor = fields.Selection(related='articulo_id.tipo_autor', string='Tipo Autor', readonly=True)
    filenameArt = fields.Char('FilenameObv', default = 'articulo.pdf')
    articulo_archivo = fields.Binary(related='articulo_id.archivo', string='Archivo', readonly=True)
    articulo_archivoDiff_m = fields.Binary(related='articulo_id.archivo_diff_m', string='Archivo Diferencias', readonly=True)
    filenameDiff = fields.Char('FilenameDiff', default = 'diferencias.pdf')
    
    @api.one
    @api.depends('articulo_nombre')
    def get_display_name(self):
        self.display_name = self.articulo_nombre

    @api.one
    def aceptar(self):
        self.write({ 'state' : 'send' })       
               
    @api.one    
    def rechazar(self):
        if self.observaciones == None:
            raise osv.except_osv(_('Warning!'), _("Es necesario añadir un archivo con las observaciones para rechazar el articulo."))
        else:
            self.write({ 'state' : 'cancel'})
            vals = {'seccion_id':self.seccion_id.id,
                    'archivo': self.articulo_id.archivo, 
                    'filename':self.articulo_id.filename, 
                    'name':self.articulo_id.name,
                    'tipo_articulo':self.articulo_id.tipo_articulo, 
                    'tipo_autor':self.articulo_id.tipo_autor,
                    'palabras_clave':self.articulo_id.palabras_clave, 
                    'user_id':self.env.user.id, 
                    'old_maquetacion_id':self.id,
                    'state':'version_rechazada'}
            self.env['articulo'].create(vals)
            self.articulo_id.write({ 'state' : 'rechazado_en_maquetacion','archivo_diff_m':None })
