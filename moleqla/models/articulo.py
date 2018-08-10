# -*- encoding: utf-8 -*-
from openerp import fields, models, api
from openerp.exceptions import ValidationError

class articulo(models.Model):
    
    _name = "articulo"
    _description = "Articulo"
    _inherit = "mail.thread"
    
    name = fields.Char('Titulo', size=128, required=True)
    tipo_autor = fields.Selection([('interno', 'Interno'), ('externo', 'Externo')], string='Tipo de Autor', required=True)
    tipo_articulo = fields.Selection([('divulgativo', 'Divulgativo'), ('investigacion', 'Investigación')], 'Tipo de Artículo', required=True)
    archivo = fields.Binary(string='Articulo PDF', required=True)
    filename = fields.Char()
    descripcion = fields.Text('Resumen')
    palabras_clave = fields.Text('Palabras Claves')    
    partner_id = fields.Many2one('res.partner', 'Author', related='user_id.partner_id', readonly=True)
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user and self.env.user.id or False)
    seccion_id = fields.Many2one('seccion', 'Sección')
    state = fields.Selection([('borrador', 'Borrador'), ('enviado', 'Enviado a Revision'), ('rechazado_en_revision', 'Rechazado en revision'),
                              ('maquetando', 'En Maquetación'), ('rechazado_en_maquetacion', 'Rechazado en Maquetacion'), ('maquetado', 'Maquetado')]
                              , 'Estado del Artículo', default='borrador')
    revision_id = fields.Many2one('revision', 'Revision')    
    revision_observaciones = fields.Binary(related='revision_id.observaciones', string='Observaciones', readonly=True)
    filenameObv = fields.Char(related='revision_id.filenameObv')
    revision_comentarios = fields.Text(related='revision_id.comentarios', string='Comentarios', readonly=True)
    maquetacion_id = fields.Many2one('maquetacion', 'Maquetación')
    maquetacion_observaciones = fields.Binary(related='maquetacion_id.observaciones', string='Observaciones', readonly=True)
    maquetacion_comentarios = fields.Text(related='maquetacion_id.comentarios', string='Comentarios', readonly=True)
    old_revision_id = fields.Many2one('revision', 'Revision')
    old_maquetacion_id = fields.Many2one('maquetacion', 'Maquetacion')    
    fecha_maq = fields.Date('Fecha de Aceptación')
    destacado = fields.Boolean('Destacado')
    premiado = fields.Boolean('Premiado')
    asignatura = fields.Char('Asignatura')
    tipo_autor_interno = fields.Selection([('libre', 'Libre'), ('asignatura', 'Asignatura')],'Tipo de Autor Interno')
    mostrar_tipo_autor_interno = fields.Boolean("Muestra tipo autor interno", compute='get_mostrar_tipo_autor_interno')
    mostrar_asignatura = fields.Boolean("Muestra asignatura", compute='get_mostrar_asignatura')
    archivo_diff = fields.Binary(string='Articulo PDF Diferencias Revision', required=True)  
    filenameDiff = fields.Char()   
    archivo_diff_m = fields.Binary('Articulo PDF Diferencias Maquetacion', required=True)      
    filenameDiff_m =  fields.Char()
    a_publicar = fields.Boolean('Aceptado para publicar')


    @api.depends('tipo_autor')
    @api.one
    def get_mostrar_tipo_autor_interno(self):
        self.mostrar_tipo_autor_interno = self.tipo_autor == 'interno'
    
    @api.depends('tipo_autor_interno')
    @api.one
    def get_mostrar_asignatura(self):
        self.mostrar_asignatura = self.tipo_autor_interno == 'asignatura'

    @api.model
    def create(self, vals):
        vals.update({
            'user_id': self.env.user.id,
            })
        return super(articulo, self).create(vals)      
    
    @api.constrains('filename')
    def _check_filename(self):
        if self.archivo:
            if not self.filename:
                raise ValidationError("No hay artículo subido")
            else:
                # Check the file's extension
                tmp = self.filename.split('.')
                ext = tmp[len(tmp)-1]
                if ext != 'pdf':
                    raise ValidationError("El artículo de subirse en formato PDF")


    @api.constrains('filenameDiff')
    def _check_filename(self):
        if self.archivo_diff:
            if not self.filenameDiff:
                raise ValidationError("No hay artículo subido")
            else:
                # Check the file's extension
                tmp = self.filenameDiff.split('.')
                ext = tmp[len(tmp)-1]
                if ext != 'pdf':
                    raise ValidationError("El artículo de subirse en formato PDF")

    
    @api.constrains('filenameDiff_m')
    def _check_filename(self):
        if self.archivo_diff_m:
            if not self.filenameDiff_m:
                raise ValidationError("No hay artículo subido")
            else:
                # Check the file's extension
                tmp = self.filenameDiff_m.split('.')
                ext = tmp[len(tmp)-1]
                if ext != 'pdf':
                    raise ValidationError("El artículo de subirse en formato PDF")

    
    @api.one
    def enviar(self):

        revisor = self.env['revision'].search([('seccion_id', '=', self.seccion_id.id)])

        if ((self.state) == ('borrador')):
            vals = {'articulo_id': self.id, 'seccion_id':self.seccion_id.id, 'revisor_id':self.revision_id.id}
            revision = self.env['revision'].create(vals)
            self.write({ 'state' : 'enviado' , 'revision_id': revision.id})

        if ((self.state) == ('rechazado_en_revision')):
            if self.archivo_diff == None:
                raise ValidationError("Es necesario añadir el articulo modificado.Por favor, edite el artículo y añada un documento.")
            else:
                revision = self.env['revision'].search([('articulo_id', '=', self.id)])
                self.write({ 'state' : 'enviado' })
                revision.write({ 'state' : 'en_revision' ,'observaciones':None})

        if ((self.state) == ('rechazado_en_maquetacion')):
            maquetacion = self.env['maquetacion'].search([('articulo_id', '=', self.id)])
            self.write({ 'state' : 'maquetando' })
            maquetacion.write({ 'state' : 'en_maquetacion' ,'observaciones':None})
    
    @api.one
    def reenviar(self):
        return self.enviar()