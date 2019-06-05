""" get venue name from given venue id."""
import requests


class ApiRequest():
    """ listen server response. """

    def __init__(self):
        self.headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        self.first_url = "https://api-dev.myg8way.com/api/v1"
        self.login_url = "/accounts/login"
        self.venue_url = "/venueProperties/"

    def get_auth_code(self):
        """step_2.1.0: for accessing jwt token. """
        # {"username":"demo_so_user@venueengage.co.za", "password":"demo9993"}

        requests_body = {
            "username": "demo_so_user@venueengage.co.za",
            "password": "demo9993"
        }
        r = requests.post(self.first_url + self.login_url, json=requests_body)
        try:
            auth_token = r.json()['jwt']
            return auth_token
        except Exception as e:
            print("Error occured !! Response auth api => {}".format(e))
            return None

    def get_venue_info(self, ve_id):
        """get building id from venue. """

        venue_api = self.first_url + self.venue_url
        self.headers['Authorization'] = "Bearer " + self.get_auth_code()
        res = requests.get(venue_api, headers=self.headers)
        data_received = res.json()
        ve_name = data_received.get("venue_properties").get(ve_id)
        if ve_name is not None:
            ve_name = ve_name.get('NAME', None)
        print("response veneue id:: {}".format(ve_name))
        return ve_name
