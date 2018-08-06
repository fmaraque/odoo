# -*- encoding: utf-8 -*-
from openerp.osv import fields, osv
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
#===============================================================================
#Con fichero adjunto
# from email.MIMEBase import MIMEBase
# from email import Encoders
# import os
#===============================================================================

class correo(osv.osv):
    
    _name = "correo"
    _description = "Correo"
    
    _columns = {
        'emailnotificacion' : fields.char('Email', size=128),
        'passwordnotificacion': fields.char('Password', size=128),
        }
    
    def password_change(self, cr, uid, ids, password, context = None):
        return {'value': {'passwordnotificacion':password},}
    
    def mail(self, cr, uid, to, subject, text):#, attach):
        #=======================================================================
        # Si el destinario es admin, no se enviara correo a menos que 
        # mas adelante se diga lo contrario
        #=======================================================================
        if to != 'admin':
            context = None
            correo = self.browse(cr, 1, 1, context)
            #correo_obj = self.pool.get('correo')
            #correo = self.search(cr, uid, [('id', '=', 1)])
            
            gmail_user = correo.emailnotificacion
            gmail_pwd = correo.passwordnotificacion
            
            msg = MIMEMultipart()
            
            msg['From'] = gmail_user
            msg['To'] = to
            msg['Subject'] = subject
            
            msg.attach(MIMEText(text, 'html'))
            
            
            #part = MIMEBase('application', 'octet-stream')
            #part.set_payload(open(attach, 'rb').read())
            #Encoders.encode_base64(part)
            #part.add_header('Content-Disposition','attachment; filename="%s"' % os.path.basename(attach))
            #msg.attach(part)
            
            
            mailServer = smtplib.SMTP("smtp.gmail.com", 587)
            mailServer.ehlo()
            mailServer.starttls()
            mailServer.ehlo()
            mailServer.login(gmail_user, gmail_pwd)
            mailServer.sendmail(gmail_user, to, msg.as_string())
            # Should be mailServer.quit(), but that crashes...
            mailServer.close()
            print "Correo enviado"
correo()