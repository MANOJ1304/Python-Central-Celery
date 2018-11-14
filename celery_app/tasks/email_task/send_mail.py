# import sys
# if sys.version_info[0] > 2:
#     from .tasks import HighTask
# else:
#     from tasks import HighTask


from tasks.celery_queue_tasks import ZZQHighTask
import smtplib
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText
from email.mime import multipart
from email.mime import text



class SendMail(ZZQHighTask):
    """ testing Task. """
    name = 'Send Mails'
    description = ''' Sending mails to user.'''
    public = True

    def run(self, *args, **kwargs):
        # print("\nENTER IN RUN METHOD")
        self.send_mail(args[0], args[1], args[2], args[3], args[4])
        return True

    def send_mail(self, sender, s_password, recipient, sub, template):
        # print ("\n\n SEND MAIL IN CC")

        msg = multipart.MIMEMultipart('alternative')
        # msg = MIMEMultipart('alternative')
        msg['Subject'] = sub
        msg['From'] = sender
        msg['To'] = recipient

        # text_m = "Hi!\nHow are you?\nHere is the link you wanted:\nhttp://www.python.org"
        html = template

        # part1 = MIMEText(text_m, 'plain')
        # part2 = MIMEText(template, 'html')
        part2 = text.MIMEText(template, 'html')

        # msg.attach(part1)
        msg.attach(part2)

        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login(sender, s_password)
        s.sendmail(sender, recipient, msg.as_string())
        s.quit()