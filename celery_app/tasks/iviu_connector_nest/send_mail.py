import smtplib
import yaml
import os
config_file = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'yml_config.yaml')

class MailSender():
    def __init__(self):
        with open(config_file, 'r') as ymlfile:
            self.cfg = yaml.load(ymlfile)

        self.username = self.cfg['mail']['username']
        self.password = self.cfg['mail']['password']
        self.emails = self.cfg['mail']['emails']


    def send_mails(self, body_text):
        server = smtplib.SMTP(self.cfg['mail']['smtp'], 587)
        server.starttls()
        server.login(self.username, self.password)

        subject = "Enter subject"
        # body_text = "mail body \n\n thanks \n\n demo_user@gmail.com"
        BODY = "\r\n".join(
        ["From: %s" % self.username,
        "To: %s" % ', '.join(self.emails),
        "Subject: %s" % subject,
        "",
        body_text])
        server.sendmail(self.username, self.emails, BODY)
        server.quit()

