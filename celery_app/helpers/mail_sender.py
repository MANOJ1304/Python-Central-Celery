import yaml
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.headerregistry import Address
from email.message import EmailMessage
import base64
from string import Template
from jinja2 import Environment, FileSystemLoader
from email.mime.application import MIMEApplication


def read_template(filename):
    with open(filename, 'r', encoding='utf-8') as template_file:
        template_file_content = template_file.read()
    # print('template_file_content ', template_file_content)
    return template_file_content

def send_mail(receivers_mail, attachment, mail_content, subject, root_path,  reply_to = None):
    with open(os.getcwd()+'/configs/config.yaml') as yamlfile:
        cfg = yaml.load(yamlfile)
        sender_address = cfg['mail_config']['username']
        sender_pass = cfg['mail_config']['password']
        receiver_address = receivers_mail

        env = Environment( loader=FileSystemLoader('{}/templates'.format(root_path)))

        # message_template = read_template('{}/templates/mail.html'.format(root_path))
        template = env.get_template('mail.html')
        message_template = template.render()
        
        #Setup the MIME
        message = MIMEMultipart('alternative')
        # message = EmailMessage()
        # message['From'] =  Address(cfg['mail_config']['name'], sender_address).
        message['From'] =  sender_address
        message['To'] = receiver_address
        message['Subject'] = subject
        message.preamble = "Your mail reader does not support report format."

        #The subject line
        #The body and the attachments for the mail
        message.add_header('reply-to', reply_to)

        mail_msg = MIMEText(message_template, 'html')
        # raw = base64.urlsafe_b64encode(mail_msg.as_string().encode('UTF-8')).decode('ascii')


        # message.attach(MIMEText(mail_content, 'html'))
       
        # message.attach(mail_msg)
        # print('message ', message)

        # Start Pdf part

        attach_file_name = attachment
        attach_file = open(attach_file_name, 'rb') # Open the file as binary mode
        payload = MIMEBase('application', 'octate-stream')
        # payload = MIMEApplication(attach_file.read(),_subtype="pdf")
        
        payload.set_payload((attach_file).read())
        encoders.encode_base64(payload) #encode the attachment
        
        # #add payload header with filename
        payload.add_header('Content-Decomposition', 'attachment', filename=attach_file_name)
        
        
        message.attach(payload)
        message.attach(mail_msg)
        # message.attach(attach_file.read())
        # message.attach(MIMEText(open(attachment).read().decode('utf-8')))

        # End Pdf part

        #Create SMTP session for sending the mail
        session = smtplib.SMTP(cfg['mail_config']['server'], cfg['mail_config']['port']) #use gmail with port
        session.starttls() #enable security
        session.login(sender_address, sender_pass) #login with mail_id and password
        # session.send_message(message)
        text = message.as_string()
        session.sendmail(sender_address, receiver_address, text)
        session.quit()
        print('Mail Sent')

def send_email_message(receivers_mail, attachment, mail_content, subject, report_data, reply_to = None, bcc = [], receivers = []):
    with open(os.getcwd()+'/configs/config.yaml') as yamlfile:
        cfg = yaml.load(yamlfile, Loader=yaml.FullLoader)
        sender_address = cfg['mail_config']['username']
        sender_pass = cfg['mail_config']['password']
        receiver_address = receivers_mail

        env = Environment( loader=FileSystemLoader('{}/templates'.format(report_data['root_path'])))

        # message_template = read_template('{}/templates/mail.html'.format(root_path))
        template = env.get_template('mail.html')
        message_template = template.render(report_data)
        

        msg = EmailMessage()
        msg.add_alternative(message_template, subtype='html')
        print('Email template added')
        
        fp = open(attachment, 'rb')
        
        pdf_data = fp.read()
        print('Pdf file read')
        ctype = 'application/octet-stream'
        maintype, subtype = ctype.split('/', 1)
        msg.add_attachment(pdf_data, maintype=maintype, subtype=subtype, filename='weekly_report.pdf')
        
        print('Pdf attachment added')

        # msg['From'] = sender_address
        msg['From'] =  Address(cfg['mail_config']['name'], "no-reply", 'tesinsights.com')
        msg['To'] = receiver_address
        msg['Subject'] = subject
        msg.add_header('reply-to', reply_to)

        print('Creating connection')
        s = smtplib.SMTP(cfg['mail_config']['server'], cfg['mail_config']['port'])

        s.starttls()

        s.login(sender_address, sender_pass)
        final_rec = receivers + bcc
        s.send_message (to_addrs=final_rec, msg=msg)
        # s.send
        s.quit()
        print('Mail Sent')