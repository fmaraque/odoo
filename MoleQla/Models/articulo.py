# -*- encoding: utf-8 -*-
from openerp import fields, models, api

class articulo(models.Model):
    
    _name = "articulo"
    _description = "Articulo"
    _inherit = "mail.thread"
    
    nombre = fields.Char('Titulo', size=128, required=True)
    display_name = fields.Char(compute='get_display_name')
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
    numero_id = fields.Many2one('numero', 'Número')
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
        if 'user_id' in vals.keys():  
            vals['user_id'] = 1
        else:
            vals['user_id'] = self.env.user.id
            nombre = vals['nombre'] + '.pdf'      
            vals['filename'] = nombre
        #TODO: Why?
        return super(articulo, self).create(vals)      
        
    
    @api.one
    def enviar(self):
        estado = ""
        articulo = self
        maquetacion_obj = self.env['maquetacion']
        
        #DAO res.users
        user_obj = self.env['res.users']
        editor_obj = self.env['editor']
        revision_obj = self.env['revision']
        revisor = editor_obj.sudo().search([('seccion_id', '=', self.seccion_id.id)])
        if ((self.state) == ('borrador')):
            vals = {'articulo_id': self.id, 'seccion_id':self.seccion_id.id, 'revisor_id':revisor.user_id.id}
            revision = self.env['revision'].sudo().create(vals)
            self.sudo().write({ 'state' : 'enviado' , 'revision_id': revision.id})
            estado = "enviado"
                       
            
        if ((articulo.state) == ('rechazado_en_revision')):
            revision = revision_obj.sudo().search([('articulo_id', '=', articulo.id)])
            self.sudo().write({ 'state' : 'enviado' })
            revision.sudo().write({ 'state' : 'start' ,'observaciones':None})
            estado = "enviado"
           
            
        if ((articulo.state) == ('rechazado_en_maquetacion')):
            maquetacion = maquetacion_obj.sudo().search([('articulo_id', '=', articulo.id)])
            self.sudo().write({ 'state' : 'maquetando' })
            maquetacion.sudo().write({ 'state' : 'start' ,'observaciones':None})
            estado = "en maquetacion"
            maquetador_obj = self.env['maquetador']
            maquetador = maquetador_obj.sudo().search([('seccion_id', '=', articulo.seccion_id.id)])
            
           
    
    @api.depends('nombre')
    @api.multi
    def get_display_name(self):
        for record in self:
            record.display_name = record.nombre
        
articulo()
