"""
mail-receiver --config '{"public_key":"M83zoNhtdKCrROILD4@5EkyhyY4R2nPNFtiT0Psnt6Dvcv9h2ci-07xc0qiBU|qe","cid":"57ebdb7bcf96483ea7b0d2ddaef14245","void":"e9ace248c67c4b62a4b44b37701f1971","smtp":{"port":587,"credentials":{"username":"abc@gmail.com","password":"pwd"},"incoming_server":"smtp.gmail.com","outgoing_server":"imap.gmail.com"},"filter_for_guest":{"tag":{"$elemMatch":{"$eq":"reconnect"}},"valid_email":{"$ne":false},"agree_newsletter":{"$ne":false}},"newsletter_html":"","spid":"5203363f47bc4c2991a7a2bf3f4a2cb4","utc_publish_date":"2017-12-11 07:38:19+00:00","veid":"06bd0fd290344b1d847695789218a5bd","subject":"Reconnect with Newtown Junction Mall"}' config_json

"""


class Utils(object):
    """ contant variables kept here."""
    login_username = "sushilj@intelipower.co.za"
    login_password = "hello"
    login_rest_api = "/api/v1/accounts/login"
    main_header = {'Content-Type':'application/json', 'Accept':'application/json'}
    patch_data = {"valid_email": "false"}
    api_name = "guests"
    news_api_name = "newsletterLogs"
    end_rest_api = "/api/v1/serviceProviders/{}/venueOwners/{}/venues/{}/{}/{}"
    list_end_rest_api = "/api/v1/serviceProviders/{}/venueOwners/{}/venues/{}/{}?where={}"

    # # __ fatti db
    front_rest_api = "https://api.fattiengage.com"
    mongo_credential = {
        "mongo_ip": "10.28.28.3",
        "mongo_port": 27017,
        "auth_user": "superuser",
        "auth_pwd": "12345678",
        "db_name": "admin",
        "collection_name": "sent_mail_record"
    }

    # # __ local 42 db
    # front_rest_api = "http://192.168.0.42"
    # mongo_credential = {
    #     "mongo_ip": "192.168.0.53",
    #     "mongo_port": 27017,
    #     "auth_user": "superuser",
    #     "auth_pwd": "12345678",
    #     "db_name": "admin",
    #     "collection_name": "sent_mail_record"
    # }
    # #__
