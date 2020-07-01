# import sys
# if sys.version_info[0] > 2:
#     from .tasks import HighTask
# else:
#     from tasks import HighTask


from tasks.celery_queue_tasks import ZZQLowTask
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
# from email.mime import multipart
# from email.mime import text



class SendMailcl(ZZQLowTask):
    """ testing Task. """
    name = 'Send Mails CL'
    description = ''' Sending mails to user.'''
    public = True
    autoinclude = True

    # templates_body  = {
    #     "73193" : "Hi {},  Opened at {} please make sure your display is switched on.",
    #     "73414" : "Hi {},  Closed at  {}",
    #     "73415":"Hi {} , Occupancy Alert -->  Current: {}   Safe Level: {}",
    #     "73416": "Hi {} , System Alert -->  {} {} is {}"
    # }
    template_subject = {
        "subject" : "TCM Alert {} - {} - {}"
    }

    def run(self, *args, **kwargs):
        # print("\nENTER IN RUN METHOD")
        self.send_mail(args[0],self.template_subject)
        return True

    def send_mail(self, venue_info,template_sub):
        sender = venue_info["sender"]
        s_password = venue_info["password"]
        recipient = venue_info["recipient"]
        sub = venue_info["sub"]
        template_body = venue_info["email_template"]
        # template = config["template"]
        message_type = venue_info["message_type"] 

        body_data = template_body
        if int(message_type) == 1:
            body_data = body_data.format( 
                             venue_info["message_info"]["full_name"],
                             venue_info["message_info"]["open_time"])
        elif int(message_type) == 2:
            body_data = body_data.format(
                             venue_info["message_info"]["full_name"],
                             venue_info["message_info"]["close_time"])
        elif int(message_type) == 3:
            body_data = body_data.format(
                             venue_info["message_info"]["full_name"],
                             venue_info["message_info"]["occupancy_count"],
                             venue_info["message_info"]["occupancy_threshold"])                             
        elif int(message_type) == 4:
            body_data = body_data.format(
                             venue_info["message_info"]["full_name"],
                             venue_info["message_info"]["area_alias"],
                             venue_info["message_info"]["device_type"],
                             venue_info["message_info"]["status"])


        subject = self.template_subject["subject"].format(
                        venue_info["message_info"]["venue_owner_alias"],
                        venue_info["message_info"]["site_alias"],
                        venue_info["message_info"]["zone_alias"])
 

        # print ("\n\n SEND MAIL IN CC")

        # msg = multipart.MIMEMultipart('alternative')
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = recipient

        # text_m = "Hi!\nHow are you?\nHere is the link you wanted:\nhttp://www.python.org"
        # html = template

        part1 = MIMEText(body_data, 'plain')
        # part2 = MIMEText(template, 'html')
        # part2 = text.MIMEText(template, 'html')

        msg.attach(part1)
        # msg.attach(part2)

        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login(sender, s_password)
        s.sendmail(sender, recipient, msg.as_string())
        s.quit()