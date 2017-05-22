#!/usr/bin/env python
# -*- coding: utf8 -*-
"""
This module provides email sending methods.
"""
import smtplib
import socket
import os
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage


def formato_string(linea):
    if isinstance(linea, unicode):
        return linea.encode('utf-8')
    else:
        return linea


def send_mail_alert(mail_text, module=__name__, recipients=(
    "rodrygoo993@gmail.com", "diegma33@gmail.com", "rlaguna@idatha.com", "rodryeluno@hotmail.com"), images=None,
                        subject="Alerta - Cosota puede estar apagada"):

    recipients = list(recipients)

    if images is None:
        images = []
    host = 'smtp.gmail.com'
    port = '587'
    user = 'pgtk90@gmail.com'
    passw = 'spectrumROOT'

    server = smtplib.SMTP()
    server.connect(host, port)
    server.ehlo()
    server.starttls()

    server.login(user, passw)

    mail_text += formato_string(u"\n\n\tMail generado el día ") + formato_string(datetime.datetime.now().strftime("%d-%m-%Y hora %H:%M:%S"))
    mail_text += formato_string(u"\n\n\tEjecutado en ") + formato_string(socket.gethostname())

    my_ip = socket.gethostbyname(socket.getfqdn())

    sender = "Spectrum pgtk90"

    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ", ".join(recipients)

    # Create the body of the message (a plain-text and an HTML version).
    plain = '''
    Descripción de la alerta:

    %s
    ''' % formato_string(mail_text)

    html = """\
    <html>
      <head>
      <style>
      </style>
      </head>
      <body>
      <div id="main" style="border:1px solid; margin: 0 auto; width: 600px; padding: 12px; border-radius:4px">
    <div id="header" style="float:none; padding:5px;">
      <div id="logo" style="float: left;"><img style="max-height:90px" src="cid:image0"></img></div>
      <div id="title" style="height:55px; margin-top: 35px; margin-left: 30px;float:left; font-family:Verdana; font-weight:bold; font-size:16px;">M&oacute;dulo de alertas autom&aacute;ticas</div>
      <div style="clear:both"></div>
    </div>
    <div style="height:1px; background-color:#888; margin-bottom:8px; margin-top:8px"></div>
    <div id="footer" style="color: #333; font-size:12px">
    <div>
      <p>%s</p>
    </div>
    <div style="height:1px; background-color:#888; margin-bottom:8px"></div>
    <div id="footer" style="color: #555; font-size:10px">
      Esta es una alerta autom&aacute;tica generada por el m&oacute;dulo <span style='font-weight:bold'>%s</span>. Enviado desde %s.
    </div>
      </div>
      </body>
    </html>
    """ % (mail_text.replace('\r\n','<br/>').replace('\n','<br/>'),module, my_ip)

    dirpath = os.path.dirname(__file__)
    imgfile = os.path.join(dirpath, 'logo.png')
    fp = open(imgfile, 'rb')
    msg_image = MIMEImage(fp.read())
    fp.close()
    # Define the image's ID as referenced above
    msg_image.add_header('Content-ID', '<image0>')

    msg_extra_images = []
    for idx, img in enumerate(images):
        fp = open(img, 'rb')
        msg_extra_image = MIMEImage(fp.read())
        fp.close()
        msg_extra_image.add_header('Content-ID', '<image'+str(idx+1)+'>')
        msg_extra_images.append(msg_extra_image)

    # Record the MIME types of both parts - text/plain and text/html.
    msg_plain = MIMEText(plain, 'plain')
    msg_html = MIMEText(html, 'html')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(msg_plain)
    msg.attach(msg_html)
    msg.attach(msg_image)
    for ex_img in msg_extra_images:
        msg.attach(ex_img)

    # Send the message via local SMTP server.
    # s = smtplib.SMTP('localhost')
    # sendmail function takes 3 arguments: sender's address, recipient's address
    # and message to send - here it is sent as one string.
    server.sendmail(sender, recipients, msg.as_string())
    server.quit()

if __name__ == '__main__':
    print "probamos enviar el mail..."
    send_mail_alert('Mensaje de prueba, Cambiando el asnunto')
    print "Final de la ejecucion."
