# -*- encoding: utf-8 -*-
from openerp import fields, models, api

class maquetacion(models.Model):
    
    _name = "maquetacion"
    _description = "Maquetacion"
    _inherit = "mail.thread"
          
    articulo_id = fields.Many2one('articulo', 'Artículo')
    seccion_id = fields.Many2one('seccion', 'Sección')
    observaciones = fields.Binary('Observaciones')
    filenameObv = fields.Char('FilenameObv', default='observaciones.pdf')
    #TODO. There is no maquetador model. There is a group which is maquetador
    #'maquetador_id': fields.integer('Maquetador')
    state = fields.Selection([('start', 'En Maquetación'), ('send', 'Maquetado'), ('cancel', 'Rechazado')], 'Estado de la maquetación', default='start')
    comentarios = fields.Text('Comentarios')
    versiones_anteriores = fields.One2many('articulo', 'old_maquetacion_id', 'Versiones anteriores')
    articulo_nombre = fields.Text(related='articulo_id.nombre', string='Nombre', readonly=True)
    articulo_descripcion = fields.Text(related='articulo_id.descripcion', string='Descripción', readonly=True)
    #I dont know if this conversion is well done
    articulo_seccion = fields.Many2one(related='articulo_id.seccion_id', string='Sección', relation='seccion', readonly=True)
    articulo_tipoArticulo = fields.Text(related='articulo_id.tipo_articulo', string='Tipo Artículo', readonly=True)
    articulo_tipoAutor = fields.Text(related='articulo_id.tipo_autor', string='Tipo Autor', readonly=True)
    filenameArt = fields.Char('FilenameObv', default = 'articulo.pdf')
    articulo_archivo = fields.Binary(related='articulo_id.archivo', string='Archivo', readonly=True)
    articulo_archivoDiff_m = fields.Binary(related='articulo_id.archivo_diff_m', string='Archivo Diferencias', readonly=True)
    filenameDiff = fields.Char('FilenameDiff', default = 'diferencias.pdf')
        
    
    @api.one
    def aceptar(self, cr, uid, ids, context=None):
        maquetacion = self.browse(cr, 1, ids, context)
        articulo_obj = self.pool.get('articulo')
        d = fields.date.today()
        articulo_obj.write(cr, 1, maquetacion.articulo_id.id, { 'state' : 'publicable', 'fecha_maq':d})
        self.write(cr, 1, ids, { 'state' : 'send' })       
               
    @api.one    
    def rechazar(self, cr, uid, ids, context=None):
        maquetacion = self.browse(cr, 1, ids, context)
        if maquetacion.observaciones == None:
            raise osv.except_osv(_('Warning!'), _("Es necesario añadir un archivo con las observaciones para rechazar el articulo."))
        else:
            self.write(cr, 1, ids, { 'state' : 'cancel'})
            articulo_obj = self.pool.get('articulo')
            articulo_id = articulo_obj.search(cr, 1, [('maquetacion_id', '=', maquetacion.id)])
            articulo = articulo_obj.browse(cr, 1, articulo_id, context)
            
            vals = {'seccion_id':maquetacion.seccion_id.id,
                    'archivo':articulo.archivo, 'filename':articulo.filename, 'nombre':articulo.nombre,
                    'tipo_articulo':articulo.tipo_articulo, 'tipo_autor':articulo.tipo_autor,
                    'palabras_clave':articulo.palabras_clave, 'user_id':1, 'old_maquetacion_id':maquetacion.id,
                    'state':'version_rechazada'}
            articulo_obj.create(cr, 1, vals, context=None)
            
            articulo_obj.write(cr, 1, maquetacion.articulo_id.id, { 'state' : 'rechazado_en_maquetacion','archivo_diff_m':None })
            
    
    
maquetacion()
