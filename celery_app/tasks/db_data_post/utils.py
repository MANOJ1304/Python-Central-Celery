""" common medhods will remain here."""
from slackclient import SlackClient


class UtilData(object):
    """ constant values kept here. """
    offset_limit = 0
    per_batch_record = 10
    # first_url = "https://api.fattiengage.com/api/v1/"
    first_url = "http://35.246.236.180/api/v1/"
    # # # tes-quiz slack keys
    # slack_info = {
    #     "token": "xoxp-561878501075-561252247888-567929287521-6eab552d9925a7510e7c7df3bd6a2eed",
    #     "channel_name": "tes-quiz"
    # }
    # # notification slack keys
    slack_info = {
        "token": "xoxp-561878501075-561252247888-562339215653-c3b30e763520d13f1c819274e30816b0",
        "channel_name": "notification"
    }

    def slack_alert(self, slack_token, channel_name, color_msg, title, msg):
        """
            get alert message on slack.
            usage: slack_alert(<slack token>, <slack channel name>" , <slack message>")
        """
        sc = SlackClient(slack_token)
        data = sc.api_call(
            "chat.postMessage",
            channel=channel_name,
            text="",
            attachments=[
                {
                    "color": color_msg,
                    "title": "Wildfire-Bocconi",
                    "title_link": "https://cms-dev.myg8way.com/#!/login",
                    # "text": msg,
                    "fields": [
                        {
                            "title": title,
                            "value": msg,
                            "short": False
                        }
                    ]
                }
            ]
        )
        return data['ok']
