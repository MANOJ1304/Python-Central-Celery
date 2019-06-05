""" common medhods will remain here."""
from slackclient import SlackClient


class UtilData():
    """common usage class. """
    socket_connection = {
        # "ip": "192.168.0.60",
        # "port": 8080,
        "ip": "35.246.245.172",
        "port": 8080,
        "params1": {
            'token': "",
            'type': 'client'
            }
        }

    filterData = {
        'floor_id': '89987c9289354ef2ae6d6fe4a4af709c',
        'filter': 'OP:MON:floorindex:Bisley:Dallington_Street:Ground_Floor',
        'e_map': {'bn': 'Dallington_Street', 'sn': 'Bisley', 'fn': 'Ground_Floor'}
        }

    chat_message = {
        "name": "location:tracker:send",
        "data": "{\"monitor\":{\"location\":{\"properties\":{\"site_index\":\"ZANAM-MAERUA MALL-Lower Level\"}}}}"
    }

    # first_url = "https://api.fattiengage.com/api/v1/"
    first_url = "http://35.246.236.180/api/v1/"
    # get_record_url = (
    #     "serviceProviders/{0}/venueOwners/{1}/venues/{2}/attendees?where="
    #     "{{\"cod_pin\": \"{3}\",\"alias_id\": \"{4}\"}}"
    # )
    get_record_url = "?where={{\"cod_pin\": \"{0}\",\"alias_id\": \"{1}\"}}"

    patch_record_url = "serviceProviders/{0}/venueOwners/{1}/venues/{2}/attendees/{3}"
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    auth_code_credential = {
        "username": "demo_so_user@venueengage.co.za",
        "password": "demo9993"
        }

    def slack_alert(self, slack_token, channel_name, msg):
        """
            get alert message on slack.
            usage: slack_alert(<slack token>, <slack channel name>" , <slack message>")
        """
        sc = SlackClient(slack_token)
        data = sc.api_call(
            "chat.postMessage",
            channel=channel_name,
            text=msg
            )
        return data['ok']
