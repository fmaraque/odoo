# -*- encoding: utf-8 -*-
from openerp import fields, models, api

class articulo(models.Model):
    
    _name = "articulo"
    _description = "Articulo"
    _inherit = "mail.thread"
    
    name = fields.Char('Titulo', size=128, required=True)
    tipo_autor = fields.Selection([('interno', 'Interno'), ('externo', 'Externo')], string='Tipo de Autor', required=True)
    tipo_articulo = fields.Selection([('divulgativo', 'Divulgativo'), ('investigacion', 'Investigación')], 'Tipo de Artículo', required=True)
    archivo = fields.Binary('Archivo', filters='*.pdf"', required=True)
    descripcion = fields.Text('Resumen')
    palabras_clave = fields.Text('Palabras Claves')
    filename = fields.Char('Filename')
    partner_id = fields.Many2one('res.partner', 'Author', related='user_id.partner_id', readonly=True)
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user and self.env.user.id or False)
    seccion_id = fields.Many2one('seccion', 'Sección')
    state = fields.Selection([('version_rechazada', 'Version rechazada'), ('borrador', 'Borrador'), ('enviado', 'Enviado'), ('rechazado_en_revision', 'En revision'),
                              ('maquetando', 'En Maquetación'), ('rechazado_en_maquetacion', 'No Maquetado'), ('publicable', 'Publicable'), ('publicado', 'Publicado'), ('rechazado_fin', 'Rechazado')]
                              , 'Estado del Artículo', default='borrador')
    revision_id = fields.Many2one('revision', 'Revision')
    revision_observaciones = fields.Binary(related='revision_id.observaciones', string='Observaciones', readonly=True)
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
    archivo_diff = fields.Binary('Archivo Diferencias', filters='*.pdf"', help="Este archivo contendrá las diferencias entre la versión antigua y la versión nuevo del artículo")  
    archivo_diff_m = fields.Binary('Archivo Diferencias', filters='*.pdf"', help="Este archivo contendrá las diferencias entre la versión antigua y la versión nuevo del artículo")      
    filenameDiff = fields.Char('FilenameDiff', default='diferencias.pdf')
    filenameObv = fields.Char('FilenameObv', default='observaciones.pdf')
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
            'filename': vals['name'] + '.pdf'
            })
        return super(articulo, self).create(vals)      

    @api.one
    def enviar(self):
        revisor = self.env['revision'].search([('seccion_id', '=', self.seccion_id.id)])
        if ((self.state) == ('borrador')):
            vals = {'articulo_id': self.id, 'seccion_id':self.seccion_id.id, 'revisor_id':revisor.revisor_id.id}
            revision = self.env['revision'].create(vals)
            self.write({ 'state' : 'enviado' , 'revision_id': revision.id})

        if ((self.state) == ('rechazado_en_revision')):
            revision = self.env['revision'].search([('articulo_id', '=', self.id)])
            self.write({ 'state' : 'enviado' })
            revision.write({ 'state' : 'start' ,'observaciones':None})

        if ((self.state) == ('rechazado_en_maquetacion')):
            maquetacion = self.env['maquetacion'].search([('articulo_id', '=', self.id)])
            self.write({ 'state' : 'maquetando' })
            maquetacion.write({ 'state' : 'start' ,'observaciones':None})
    
    @api.one
    def reenviar(self):
        return self.enviar()