import yaml
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.headerregistry import Address
from email.message import EmailMessage

def send_mail(receivers_mail, attachment, mail_content, subject, reply_to = None):
    with open(os.getcwd()+'/configs/config.yaml') as yamlfile:
        cfg = yaml.load(yamlfile)
        sender_address = cfg['mail_config']['username']
        sender_pass = cfg['mail_config']['password']
        receiver_address = receivers_mail

        #Setup the MIME
        message = MIMEMultipart('alternative')
        # message = EmailMessage()
        # message['From'] =  Address(cfg['mail_config']['name'], sender_address).
        message['From'] =  sender_address
        message['To'] = receiver_address
        message['Subject'] = subject
        
        #The subject line
        #The body and the attachments for the mail
        message.add_header('reply-to', reply_to)


        message.attach(MIMEText(mail_content, 'plain'))
        attach_file_name = attachment
        attach_file = open(attach_file_name, 'rb') # Open the file as binary mode
        payload = MIMEBase('application', 'octate-stream')
        payload.set_payload((attach_file).read())
        encoders.encode_base64(payload) #encode the attachment
        #add payload header with filename
        payload.add_header('Content-Decomposition', 'attachment', filename=attach_file_name.split('/')[-1])
        message.attach(payload)
        #Create SMTP session for sending the mail
        session = smtplib.SMTP(cfg['mail_config']['server'], cfg['mail_config']['port']) #use gmail with port
        session.starttls() #enable security
        session.login(sender_address, sender_pass) #login with mail_id and password
        # session.send_message(message)
        text = str(message.as_string())
        session.sendmail(sender_address, receiver_address, text)
        session.quit()
        print('Mail Sent')



    