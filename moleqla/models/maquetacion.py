# -*- encoding: utf-8 -*-
from openerp import fields, models, api
from openerp.osv import osv
from openerp.exceptions import ValidationError

class maquetacion(models.Model):
    
    _name = "maquetacion"
    _description = "Maquetacion"
    _inherit = "mail.thread"
    _rec_name = "articulo_nombre"

    articulo_id = fields.Many2one('articulo', 'Articulo')
    seccion_id = fields.Many2one('seccion', 'Sección')
    observaciones = fields.Binary(string='Observaciones')
    filenameObv = fields.Char()    
    maquetador_id = fields.Many2one('res.users','Maquetador', domain="[('is_maquetador', '=', True)]")
    state = fields.Selection([('en_maquetacion', 'En Maquetación'), ('rechazado_en_maquetacion', 'Rechazado en maquetacion'), ('maquetado', 'Maquetado')], 'Estado de la maquetación', default='en_maquetacion')
    comentarios = fields.Text('Comentarios')
    versiones_anteriores = fields.One2many('articulo', 'old_maquetacion_id', 'Versiones anteriores')
    articulo_nombre = fields.Char(related='articulo_id.name', string='Nombre', readonly=True, store=True)
    display_name = fields.Char(compute='get_display_name')
    articulo_descripcion = fields.Text(related='articulo_id.descripcion', string='Descripción', readonly=True, store=True)
    articulo_seccion = fields.Many2one(related='articulo_id.seccion_id', string='Sección', comodel_name='seccion', readonly=True, store=True)
    articulo_tipoArticulo = fields.Selection(related='articulo_id.tipo_articulo', string='Tipo Artículo', readonly=True, store=True)
    articulo_tipoAutor = fields.Selection(related='articulo_id.tipo_autor', string='Tipo Autor', readonly=True, store=True)    
    filenameArt = fields.Char(related='articulo_id.filename', store=True)
    articulo_archivo = fields.Binary(related='articulo_id.archivo', string='Archivo', readonly=True, store=True) 
    articulo_archivoDiff_m = fields.Binary(related='articulo_id.archivo_diff_m', store=True)    
    filenameDiff = fields.Char(related='articulo_id.filenameDiff_m', store=True)

    @api.one
    def aceptar(self):
        self.write({ 'state' : 'maquetado' })
        self.articulo_id.write({'state': 'maquetado'})              
               
    @api.one    
    def rechazar(self):
        if self.observaciones == None:
            raise ValidationError("Es necesario añadir un archivo con las observaciones para rechazar el articulo.")
        else:
            self.write({ 'state' : 'rechazado_en_maquetacion'})
            vals = {'seccion_id':self.seccion_id.id,
                    'archivo': self.articulo_id.archivo, 
                    'filename':self.articulo_id.filename, 
                    'name':self.articulo_id.name,
                    'tipo_articulo':self.articulo_id.tipo_articulo, 
                    'tipo_autor':self.articulo_id.tipo_autor,
                    'palabras_clave':self.articulo_id.palabras_clave, 
                    'user_id':self.env.user.id, 
                    'old_maquetacion_id':self.id,
                    'state':'rechazado_en_maquetacion'}
            #self.env['articulo'].create(vals)
            self.articulo_id.write({ 'state' : 'rechazado_en_maquetacion','archivo_diff_m':None })

    @api.constrains('filenameObv')
    def _check_filename(self):
        if self.observaciones:
            if not self.filenameObv:
                raise ValidationError("No hay artículo subido")
            else:
                # Check the file's extension
                tmp = self.filenameObv.split('.')
                ext = tmp[len(tmp)-1]
                if ext != 'pdf':
                    raise ValidationError("El artículo de subirse en formato PDF")