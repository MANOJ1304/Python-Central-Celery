""" celery worker -A mail_templatesender.mail_sender.celery --autoscale=20,5 -l info"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
# from email.mime.base import MIMEBase
# from email import encoders
# from jinja2 import Environment, FileSystemLoader

# from celery import Celery
# celery = Celery('mail_sender', broker='redis://localhost:6379/0')


# @celery.task
def send_mail(html_file, receiver_addr, config_json):
    """ sending mail using smtp."""

    smtp_server = config_json["smtp"]['outgoing_server']
    smtp_port = config_json["smtp"]['port']
    fromaddr = config_json["smtp"]['credentials']['username']
    mail_pwd = config_json["smtp"]['credentials']['password']
    sender_subject = config_json["subject"]
    auth_required = config_json["smtp"]['auth_required']
    reply_mail = config_json["smtp"]['reply_to']

    # # ---
    try:
        # # __ login and send1 emails
        # with open(html_file,'r') as file:
        #   HTML = file.read()
        HTML = html_file
        '''
        ##__ for sending mail with jinja template
        user_dict = {"first_name":"user",
            "mall_name":"NTG",
            "user_name":"user_tester",
            "actual_password":"xyz",
            "mall_website":"www.google.com"
            }
        HTML = Environment().from_string(HTML).render(first_name=user_dict['first_name'],
                                        mall_name=user_dict['mall_name'],
                                        user_name=user_dict['user_name'],
                                        actual_password=user_dict['actual_password'],
                                        mall_website=user_dict['mall_website']
                                )
        '''
        msg = MIMEMultipart()
        msg['From'] = fromaddr
        msg['To'] = receiver_addr
        msg['Subject'] = sender_subject
        msg['Reply-to'] = reply_mail
        # # __ send normal msg in mail body
        # body = "Hi, This is Test Mail"
        # msg.attach(MIMEText(body, 'plain'))
        msg.attach(MIMEText(HTML, 'html'))
        # # __ send file with attachement
        # filename = "template.html"
        # attachment = open(html_file, "rb")
        # part = MIMEBase('application', 'octet-stream')
        # part.set_payload((attachment).read())
        # encoders.encode_base64(part)
        # part.add_header('Content-Disposition', "attachment; filename= %s" % filename)
        # msg.attach(part)
        server = smtplib.SMTP(smtp_server, smtp_port)
        if auth_required:
            server.starttls()
            server.login(fromaddr, mail_pwd)
        text = msg.as_string()
        server.sendmail(fromaddr, receiver_addr, text)
        print("\n\t\t\t-->mail sent on mail {}<<\n".format(receiver_addr))
        server.quit()

    except Exception as e:
        print("Error in mail sender is: {}\n".format(e))
        exit()
    # # ---
    #     # server.mail(receiver_addr)
    #     # code, message = server.rcpt(str(receiver_addr))
    #     # print(code,message,receiver_addr)
