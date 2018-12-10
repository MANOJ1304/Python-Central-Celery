class UtilData():
    socket_connection = {
        "ip": "192.168.0.60",
        "port": 8080,
        "params1": {
            'token': "",
            'type': 'client'
            }
        }

    get_auth_code = {
        "username": "olivia_brown@bisley.co.uk",
        "password": "9bs9kw5a",
        "api": "http://192.168.0.42/api/v1/accounts/login"
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
