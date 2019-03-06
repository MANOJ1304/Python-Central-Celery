import smtplib
import yaml


class MailSender():
    def __init__(self, config):
        # with open(config_file, 'r') as ymlfile:
        #     self.cfg = yaml.load(ymlfile)
        # print('Mail config', config)
        self.config = config
        self.username = self.config['username']
        self.password = self.config['password']
        self.emails = self.config['emails']


    def send_mails(self, body_text):
        server = smtplib.SMTP(self.config['smtp'], 587)
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

