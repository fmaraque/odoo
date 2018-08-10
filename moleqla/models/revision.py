# -*- encoding: utf-8 -*-

from openerp import fields, models, api
from openerp.osv import osv
from openerp.exceptions import ValidationError
#Once the autor save the articulo and click on Enviar, the articulo status is Send. So if Editor goes to the revision and the artiulo belongs to its section
# The editor will see the articulo and then he can click on Accept (articulo is going to maquetacion) or in Rechazar (articulo is going back (to Send)
class revision(models.Model):
    
    _name = "revision"
    _description = "Revision"
    _inherit = "mail.thread"
        
    articulo_id = fields.Many2one('articulo','Artículo') 
    filename = fields.Char('Filename') 
    seccion_id = fields.Many2one('seccion','Sección')
    observaciones = fields.Binary(string='Observaciones')
    filenameObv = fields.Char()  
    revisor_id = fields.Many2one('res.users', 'Editor', domain="[('is_editor', '=', True)]")
    state = fields.Selection([('en_revision', 'En Revision'), ('enviado_a_maquetacion', 'A Maquetacion'), ('rechazado_en_revision', 'Rechazado en revision')], 'Estado de la revisión', default='en_revision')
    comentarios = fields.Text('Comentarios')
    versiones_anteriores = fields.One2many('articulo', 'old_revision_id','Versiones anteriores')
    articulo_nombre = fields.Char(related='articulo_id.name', string='Nombre', readonly=True)
    articulo_estado = fields.Selection(related='articulo_id.state', string='Estado del artículo', readonly=True)
    articulo_a_publicar = fields.Boolean(related='articulo_id.a_publicar', string='Artículo a publicar', type='boolean', readonly=True)
    articulo_descripcion = fields.Text(related = 'articulo_id.descripcion', string='Descripción', readonly=True)
    articulo_seccion = fields.Many2one(related='articulo_id.seccion_id', string='Sección', comodel_name='seccion', readonly=True)      
    articulo_tipoArticulo = fields.Selection(related='articulo_id.tipo_articulo', string='Tipo Artículo', readonly=True)
    articulo_tipoAutor = fields.Selection(related='articulo_id.tipo_autor', string='Tipo Autor', readonly=True)
    filenameArt = fields.Char(related='articulo_id.filename')
    articulo_archivo = fields.Binary(related='articulo_id.archivo', string='Articulo', readonly=True)
    articulo_archivoDiff = fields.Binary(related='articulo_id.archivo_diff')
    filenameDiff = fields.Char(related='articulo_id.filenameDiff')
    maquetacion_id = fields.Many2one('maquetacion', 'Maquetacion')

    @api.one
    def aceptar(self):
        self.write({ 'state' : 'enviado_a_maquetacion' })
        vals = {'articulo_id': self.articulo_id.id, 'seccion_id': self.seccion_id.id, 'maquetador_id': self.seccion_id.maquetador.id}
        maquetacion = self.env['maquetacion'].create(vals)
        #It doesn't make sense to have articulo referenced in maquatacion and at the same time maquetacion referenced in articulo. But I'll let it be as it was
        self.articulo_id.write({'state': 'maquetando', 'maquetacion_id': maquetacion.id})        
        

    @api.one
    def rechazar(self):
        if self.observaciones == None:
            raise ValidationError("Es necesario añadir un documento con las revisiones.Por favor, edite el artículo y añada un documento.")
        else:
            self.write({ 'state' : 'rechazado_en_revision' })
            vals = {'seccion_id':self.seccion_id.id,
                    'archivo': self.articulo_id.archivo,
                    'filename': self.articulo_id.filename,
                    'name': self.articulo_id.name,
                    'tipo_articulo': self.articulo_id.tipo_articulo,
                    'tipo_autor': self.articulo_id.tipo_autor,
                    'palabras_clave': self.articulo_id.palabras_clave,
                    'user_id':self.env.user.id,
                    'old_revision_id': self.id,
                    'state':'rechazado_en_revision'
                   }
            #self.env['articulo'].create(vals)
            self.articulo_id.write({ 'state' : 'rechazado_en_revision' ,'archivo_diff':None})
               

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