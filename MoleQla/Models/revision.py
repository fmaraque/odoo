# -*- encoding: utf-8 -*-
from openerp import fields, models, api
#Once the autor save the articulo and click on Enviar, the articulo status is Send. So if Editor goes to the revision and the artiulo belongs to its section
# The editor will see the articulo and then he can click on Accept (articulo is going to maquetacion) or in Rechazar (articulo is going back (to Send)
class revision(models.Model):
    
    _name = "revision"
    _description = "Revision"
    _inherit = "mail.thread"
        
    articulo_id = fields.Many2one('articulo','Artículo') 
    filename = fields.Char('Filename') 
    seccion_id = fields.Many2one('seccion','Sección')
    observaciones = fields.Binary('Observaciones')
    filenameObv = fields.Char('FilenameObv', default='observaciones.pdf')  
    #TODO We should get the Revisor id from res.user and res.group=Editor... But how?
    #revisor_id = fields.Integer('Editor')
    state = fields.Selection([('start', 'Inicio'), ('send', 'Aceptado'), ('cancel', 'Revisando'),('cancel_2', 'Rechazado'),('published', 'A Publicar')], 'Estado de la revisión', default='start')
    comentarios = fields.Text('Comentarios')
    versiones_anteriores = fields.One2many('articulo', 'old_revision_id','Versiones anteriores')
    articulo_nombre = fields.Text(related='articulo_id.nombre', string='Nombre', readonly=True)
    articulo_estado = fields.Text(related='articulo_id.state', string='Estado del artículo', readonly=True)
    articulo_a_publicar = fields.Boolean(related='articulo_id.a_publicar', string='Artículo a publicar', type='boolean', readonly=True)
    articulo_descripcion = fields.Text(related = 'articulo_id.descripcion', string='Descripción', readonly=True)
        #'articulo_seccion' : fields.related('articulo_id', 'seccion_id', string='Sección', type='many2one', relation='seccion',readonly=True),
        #TODO. I am not sure if this conversion from fields.related to fields.many is well done
    articulo_seccion = fields.Many2one(related='articulo_id.seccion_id', string='Sección', relation='seccion',readonly=True)      
    articulo_tipoArticulo = fields.Text(related='articulo_id.tipo_articulo', string='Tipo Artículo', readonly=True)
    articulo_tipoAutor = fields.Text(related='articulo_id.tipo_autor', string='Tipo Autor', readonly=True)
    filenameArt = fields.Char('FilenameArt', default='articulo.pdf')
    articulo_archivo = fields.Binary(related='articulo_id.archivo', string='Archivo', readonly=True)
    articulo_archivoDiff = fields.Binary(related='articulo_id.archivo_diff', string='Archivo Diferencias', readonly=True)
    filenameDiff = fields.Char('FilenameDiff', default='diferencias.pdf')
    
    
    @api.one
    def aceptar(self):
        revision = self
        #I don't understand this
        self.write(cr, 1, ids, { 'state' : 'send' })
        
        articulo_obj = self.env['articulo']
        
        #TODO All this stuff will change since we will delete maquetador Model. How could I get the user which has Maquetador group¿???
        maquetador_obj = self.env['maquetador']
        maquetador_id = maquetador_obj.search(cr, 1, [('seccion_id', '=', revision.seccion_id.id)])
        maquetador = maquetador_obj.browse(cr, 1, maquetador_id, context)
        
        #TODO I do not know how to update
        vals = {'articulo_id':revision.articulo_id.id,'seccion_id':revision.seccion_id.id,'maquetador_id':maquetador[0].user_id.id}
        
        
        maquetacion_obj = self.env['maquetacion']
        maquetacion_obj.create(cr, 1, vals,context=None)
        maquetacion_id = maquetacion_obj.search(cr, 1, [('articulo_id', '=', revision.articulo_id.id)])
        articulo_obj.write(cr, 1, revision.articulo_id.id, { 'state' : 'maquetando', 'maquetacion_id':maquetacion_id[0] })        
        
    @api.one
    def rechazar(self):
        revision = self.browse(cr, 1, ids, context)
        if revision.observaciones == None:
            raise osv.except_osv(_('Warning!'), _("Es necesario añadir un archivo con las observaciones para rechazar el articulo."))
        else:
            self.write(cr, 1, ids, { 'state' : 'cancel' })
            articulo_obj = self.pool.get('articulo') 
            articulo_id = articulo_obj.search(cr, 1, [('revision_id', '=', revision.id)])
            articulo = articulo_obj.browse(cr, 1, articulo_id, context)
            
            vals = {'seccion_id':revision.seccion_id.id,
                    'archivo':articulo.archivo,'filename':articulo.filename,'nombre':articulo.nombre,
                    'tipo_articulo':articulo.tipo_articulo,'tipo_autor':articulo.tipo_autor,
                    'palabras_clave':articulo.palabras_clave,'user_id':1,'old_revision_id':revision.id,
                    'state':'version_rechazada'}
            articulo_obj.create(cr, 1, vals, context=None)
            articulo_obj.write(cr, 1, revision.articulo_id.id, { 'state' : 'rechazado_en_revision' ,'archivo_diff':None})
            
    @api.one
    def publicarArt(self):
        revision = self.browse(cr, 1, ids, context)
        articulo_obj = self.pool.get('articulo')   
        seccion_obj = self.pool.get('seccion') 
        max = seccion_obj.browse(cr,1,revision.seccion_id.id).max_articulos
        articulos_a_publicar =  articulo_obj.search(cr, 1, [('seccion_id', '=', revision.seccion_id.id),('a_publicar','=', 'TRUE'),('state','!=', 'publicado')])
        if len(articulos_a_publicar)< max:    
            self.write(cr, 1, ids[0], { 'state' : 'published'})
            articulo_obj.write(cr, 1, revision.articulo_id.id, { 'a_publicar' : 'TRUE'})
        else:
            raise osv.except_osv(_('Warning!'), _("No se pueden publicar mas articulos de esta seccion en el proximo numero."))
        
    @api.one
    def rechazar_fin(self):
        self.write(cr, 1, ids, { 'state' : 'cancel_2' })
        revision = self.browse(cr, 1, ids, context)
        articulo_obj = self.pool.get('articulo')  
              
        articulo_obj.write(cr, 1, revision.articulo_id.id, { 'state' : 'rechazado_fin'})
     
revision()
