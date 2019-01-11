""" all constant values kept here."""


class UtilData(object):
    """ all constant values kept here."""

    redis = {
        # 'host': '46.101.72.227',
        # 'port': 7777
        'host': '192.168.0.53',
        'port': 6379
    }

    api = {
        # 'prototype': 'https://',
        # 'domain_name': 'api.fattiengage.com',
        'prototype': 'http://',
        'domain_name': '192.168.0.42',
        'default_header': {"Accept": "application/json", "Content-Type": "application/json"}
    }

    urls = {
        'login': api['prototype'] + api['domain_name'] + '/api/v1/accounts/login',
        'devices': api['prototype'] + api['domain_name'] + '/api/v1/venues/devices'
    }
