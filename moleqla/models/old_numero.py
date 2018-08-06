# -*- encoding: utf-8 -*-
from openerp.osv import fields, osv
from openerp.tools.translate import _

class numero(osv.osv):
    
    _name = "numero"
    _description = "Numero"
    
    def _getUlt(self, cr, uid, ids, context=None):
        cr.execute('select MAX(numero) from numero')
        id_returned = cr.fetchone()
        
        if not id_returned[0]:
            num_numero = 1
        else:
            num_numero = id_returned[0] + 1
        
        return num_numero
    
    _columns = {
        'nombre' : fields.char('Nombre', size=128, required=True),
        'numero' : fields.integer('Numero', readonly=True),
        'premio_div' : fields.many2one('articulo', 'Premio Divulgativo'),
        'premio_inv' : fields.many2one('articulo', 'Premio Investigación'),
        'articulos_id' : fields.one2many('articulo', 'numero_id', 'Artículos'),
        'fecha_p' : fields.date('Fecha de Publicación', required=True),
        'fecha_d' : fields.date('Fin Proceso Art.Destacados'),
        'fecha_v' : fields.date('Fin Votaciones'),
        'state':fields.selection([('start', 'Borrador'), ('builded', 'En construcción'), ('a_publicar', 'Publicada'), ('voted', 'En votación'), ('closed', 'Cerrado')], 'Estado del número'),
        'entrevista': fields.binary('Entrevista', filters='*.pdf"'),
        'filenameEnt': fields.char('FilenameEnt'),
        }
    
    _defaults = {
                  'state':'start',
                  'numero': _getUlt,
                  'filenameEnt':'entrevista.pdf'
                  }
    
    _order = 'state desc, id desc'
    
    def create(self, cr, uid, vals, context=None):
        numero_obj = self.pool.get('numero')
        numeros_start = numero_obj.search(cr, 1, [('state', '=', 'start')])
        numeros_builded = numero_obj.search(cr, 1, [('state', '=', 'builded')])
        #hoy = fields.date.today()       
        #fec = vals['fecha_p']
        
        #=======================================================================
        # if fec < hoy:
        #     raise osv.except_osv(_('Warning!'),_("La fehca de publicacion no puede ser menor a la del dia de hoy."))
        # else:
        #=======================================================================
        if not numeros_start:      
            if not numeros_builded:    
                    # -------------------------------------------
                # Correo a cada uno de los editores
                #2. Mediante el articulo    
                # Obtenemos el editor de seccion
                fecha = vals['fecha_p']
                editor_obj = self.pool.get('editor')
                user_obj = self.pool.get('res.users')
                editores = editor_obj.search(cr, 1, [('id', '>', 0)])
                for editor in editores:
                    editor_ = editor_obj.browse(cr, 1, editor, context)
                    user_editor = user_obj.browse(cr, 1,editor_.user_id.id, context)
                    email_editor = user_editor.login
                    
                    # Asunto y texto del email
                    asunto = "Nuevo numero" 
                    texto = "La fecha de publicacion del nuevo numero sera el " + fecha + ". Por tanto, esta es la fecha maxima para la maquetacion de los articulos"
                    
                    # Se envia el correo
                    correo_obj = self.pool.get('correo') 
                    
                    try:       
                        correo_obj.mail(cr, 1, email_editor, asunto, texto)
                    except:
                        print "ERROR: No ha sido posible enviar el correo a"+email_editor
                    # -------------------------------------------
                maquetador_obj = self.pool.get('maquetador')
                user_obj = self.pool.get('res.users')
                maquetadores = maquetador_obj.search(cr, 1, [('id', '>', 0)])
                for maquetador in maquetadores:
                    maquetador_ = maquetador_obj.browse(cr, 1, maquetador, context)
                    user_editor = user_obj.browse(cr, 1,maquetador_.user_id.id, context)
                    email_editor = user_editor.login
                    
                    # Asunto y texto del email
                    asunto = "Nuevo numero" 
                    texto = "La fecha de publicacion del nuevo numero sera el " + fecha + ". Por tanto, esta es la fecha maxima para la maquetacion de los articulos"
                    
                    # Se envia el correo
                    correo_obj = self.pool.get('correo') 
                    
                    try:       
                        correo_obj.mail(cr, 1, email_editor, asunto, texto)
                    except:
                        print "ERROR: No ha sido posible enviar el correo a"+email_editor
                return super(numero, self).create(cr, 1, vals, context) 
            else:
                raise osv.except_osv(_('Warning!'), _("No se puede crear un numero, ya hay uno en estado 'en construccion'."))
        else:
            raise osv.except_osv(_('Warning!'), _("No se puede crear un numero, ya hay uno en estado 'en borrador'."))           
              
    
    def build(self, cr, uid, ids, context=None):
        self.write(cr, 1, ids, { 'state' : 'builded'})
        obj_articulo = self.pool.get('articulo')
        obj_seccion = self.pool.get('seccion')
        secciones = obj_seccion.search(cr, 1, [('id', '>', 0)])
        ides = []
        for seccion in secciones:
            seccion_ = obj_seccion.browse(cr, 1, seccion, context)
            ids_articulos = obj_articulo.search(cr, 1, [('a_publicar', '=', 'TRUE'),('state', '=', 'publicable'), ('seccion_id', '=', seccion_.id)])
        if len(ids_articulos) > seccion_.max_articulos:
                i = 0
                for ide in ids_articulos:
                    i = i + 1
                    if i <= seccion_.max_articulos:
                        ides.append(ide)
            else:
                for ide in ids_articulos:
                        ides.append(ide)  
                   
        obj_articulo.write(cr, 1, ides, {'numero_id' : ids[0]})
     
    def send(self, cr, uid, ids, context=None):
        obj_articulo = self.pool.get('articulo')
        articulos = obj_articulo.search(cr, 1, [('numero_id', '=', ids[0])])
        obj_articulo.write(cr, 1, articulos, { 'state' : 'publicado', })
        obj_seccion = self.pool.get('seccion')
        secciones = obj_seccion.search(cr, 1, [('id', '>', 0)])
        for seccion in secciones:
            seccion_ = obj_seccion.browse(cr, 1, seccion, context)
            ids_articulos = obj_articulo.search(cr, 1, [('state', '=', 'publicado'), ('numero_id', '=', ids[0]), ('seccion_id', '=', seccion_.id)])
            if len(ids_articulos) > 0:
                obj_revisor = self.pool.get('editor')
                editor_id = obj_revisor.search(cr, 1, [('seccion_id', '=', seccion_.id)])
                editor = obj_revisor.browse(cr, 1, editor_id, context)
                revisor_id = editor[0].user_id.id
                obj_destaque = self.pool.get('destaque_articulos')
                vals = {'seccion_id':seccion_.id, 'revisor_id':revisor_id, 'numero_id':ids[0]}
                obj_destaque.create(cr, 1, vals, context=None) 
        fecha_d =self.browse(cr, 1, ids[0])[0].fecha_d
        editor_obj = self.pool.get('editor')
        user_obj = self.pool.get('res.users')
        editores = editor_obj.search(cr, 1, [('id', '>', 0)])
        for editor in editores:
            editor_ = editor_obj.browse(cr, 1, editor, context)
            user_editor = user_obj.browse(cr, 1,editor_.user_id.id, context)
            email_editor = user_editor.login
            
            # Asunto y texto del email
            asunto = "Proceso de Destacar Articulo" 
            texto = "Se inicia el proceso de Destacar Articulos para la nueva revista publicada. El plazo es hasta " + fecha_d + "."
            
            # Se envia el correo
            correo_obj = self.pool.get('correo') 
            
            try:       
                correo_obj.mail(cr, 1, email_editor, asunto, texto)
            except:
                print "ERROR: No ha sido posible enviar el correo a"+email_editor
            # -------------------------------------------
        self.write(cr, 1, ids, { 'state' : 'a_publicar', })
        
        # Se le pone la fecha de publicacion el dia en que le da a publicar
        hoy = fields.date.today()
        self.write(cr, 1, ids, { 'fecha_p' : hoy, })
        
        
         
    def vote(self, cr, uid, ids, context=None):
        obj_editor = self.pool.get('editor')
        obj_maquetador = self.pool.get('maquetador')
        obj_votacion = self.pool.get('votacion')
        obj_articulo = self.pool.get('articulo')
        obj_linea_votacion = self.pool.get('linea_votacion')
        editores = obj_editor.search(cr, 1, [('id', '>', 0)])
        maquetadores = obj_maquetador.search(cr, 1, [('id', '>', 0)])
        articulos = obj_articulo.search(cr, 1, [('numero_id', '=', ids[0]), ('destacado', '=', 'TRUE')])  
        for editor in editores:
            editor_ = obj_editor.browse(cr, 1, editor, context) 
            vals = {}
            vals = {'user_id':editor_.user_id.id, 'numero_id':ids[0]}
            obj_votacion.create(cr, 1, vals, context=None)
            for articulo in articulos:
                articulo_ = obj_articulo.browse(cr, 1, articulo, context)
                vals_linea = {}
                votacion_id = obj_votacion.search(cr, 1, [('numero_id', '=', ids[0]), ('user_id', '=', editor_.user_id.id)])
                if articulo_.tipo_articulo == 'divulgativo':
                    vals_linea = {'votacion_div_id':votacion_id[0], 'articulo':articulo, 'filename':articulo_.filename}
                else:
                    vals_linea = {'votacion_inv_id':votacion_id[0], 'articulo':articulo, 'filename':articulo_.filename}
                obj_linea_votacion.create(cr, 1, vals_linea, context=None) 
        for maquetador in maquetadores:
            maquetador_ = obj_maquetador.browse(cr, 1, maquetador, context) 
            vals = {}
            vals = {'user_id':maquetador_.user_id.id, 'numero_id':ids[0]}
            obj_votacion.create(cr, 1, vals, context=None)
            for articulo in articulos:
                articulo_ = obj_articulo.browse(cr, 1, articulo, context)
                vals_linea = {}
                votacion_id = obj_votacion.search(cr, 1, [('numero_id', '=', ids[0]), ('user_id', '=', maquetador_.user_id.id)])
                if articulo_.tipo_articulo == 'divulgativo':
                    vals_linea = {'votacion_div_id':votacion_id[0], 'articulo':articulo}
                else:
                    vals_linea = {'votacion_inv_id':votacion_id[0], 'articulo':articulo}
                obj_linea_votacion.create(cr, 1, vals_linea, context=None)     
        fecha_v =self.browse(cr, 1, ids[0])[0].fecha_v
        editor_obj = self.pool.get('editor')
        user_obj = self.pool.get('res.users')
        editores = editor_obj.search(cr, 1, [('id', '>', 0)])
        for editor in editores:
            editor_ = editor_obj.browse(cr, 1, editor, context)
            user_editor = user_obj.browse(cr, 1,editor_.user_id.id, context)
            email_editor = user_editor.login
            
            # Asunto y texto del email
            asunto = "Premios Moleqla" 
            texto = "Se inicia el proceso de Votacion de Articulos Destacados para la nueva revista publicada. El plazo es hasta " + fecha_v + "."
            
            # Se envia el correo
            correo_obj = self.pool.get('correo') 
            
            try:       
                correo_obj.mail(cr, 1, email_editor, asunto, texto)
            except:
                print "ERROR: No ha sido posible enviar el correo a"+email_editor
            # -------------------------------------------  
        maquetador_obj = self.pool.get('maquetador')
        user_obj = self.pool.get('res.users')
        maquetadores = maquetador_obj.search(cr, 1, [('id', '>', 0)])
        for maquetador in maquetadores:
            maquetador_ = maquetador_obj.browse(cr, 1, maquetador, context)
            user_editor = user_obj.browse(cr, 1,maquetador_.user_id.id, context)
            email_editor = user_editor.login
            
            # Asunto y texto del email
            asunto = "Premios Moleqla" 
            texto = "Se inicia el proceso de Votacion de Articulos Destacados para la nueva revista publicada. El plazo es hasta " + fecha_v + "."
            
            # Se envia el correo
            correo_obj = self.pool.get('correo') 
            
            try:       
                correo_obj.mail(cr, 1, email_editor, asunto, texto)
            except:
                print "ERROR: No ha sido posible enviar el correo a"+email_editor
        self.write(cr, 1, ids, { 'state' : 'voted'})    
         
    def close(self, cr, uid, ids, context=None):
        obj_votacion = self.pool.get('votacion')
        obj_articulo = self.pool.get('articulo')
        
        votaciones_id = obj_votacion.search(cr, 1, [('numero_id', '=', ids[0]), ('state', '=', 'send')])
        puntos_div = {}
        puntos_inv = {}
        for votaciones in votaciones_id:
            votacion_ = obj_votacion.browse(cr, 1, votaciones, context)
            lineas_div = votacion_.lineas_votacion_div
            for linea in lineas_div:
                id_articulo = linea.articulo.id
                if id_articulo in puntos_div.keys():
                    puntos_div[id_articulo] = puntos_div[id_articulo] + linea.puntos
                else:
                    puntos_div[id_articulo] = linea.puntos
            lineas_inv = votacion_.lineas_votacion_inv
            for linea in lineas_inv:
                id_articulo = linea.articulo.id
                if id_articulo in puntos_inv.keys():
                    puntos_inv[id_articulo] = puntos_inv[id_articulo] + linea.puntos
                else:
                    puntos_inv[id_articulo] = linea.puntos
                    
        maximo_div = 0
        maximo_div_id = 0
        puntos_div = puntos_div.items()
        for i in range(len(puntos_div)):
            if puntos_div[i][1] > maximo_div:
                maximo_div = puntos_div[i][1]
                maximo_div_id = puntos_div[i][0]
        
        maximo_inv_id = 0            
        maximo_inv = 0
        puntos_inv = puntos_inv.items()
        for i in range(len(puntos_inv)):
            if puntos_inv[i][1] > maximo_inv:
                maximo_inv = puntos_inv[i][1]
                maximo_inv_id = puntos_inv[i][0] 
                        
        votaciones_id_vacias = obj_votacion.search(cr, 1, [('numero_id', '=', ids[0]), ('state', '=', 'start')])
         
        for votaciones in votaciones_id_vacias:
            obj_votacion.write(cr, 1, votaciones, { 'state' : 'send'})     
            
        try:   
            obj_articulo.write(cr, 1, maximo_div_id, { 'premiado' : 'TRUE'})  
            obj_articulo.write(cr, 1, maximo_inv_id, { 'premiado' : 'TRUE'})  
            self.write(cr, 1, ids, { 'state' : 'closed', 'premio_div':maximo_div_id, 'premio_inv':maximo_inv_id})
        except:
            raise osv.except_osv(_('Error!'), _("No se ha podido cerrar el numero"))
    
    def name_get(self, cr, uid, ids, context=None):
        
        if context is None:
            context = {}
        res = []
        
        for record in self.browse(cr, 1, ids, context=context):
            numero_name = record.nombre
            numero_num = record.numero
            
            string = numero_name + " (" + str(numero_num) + ")"
            
            
            res.append((record.id, string))
        return res
            
       
       
        
numero()