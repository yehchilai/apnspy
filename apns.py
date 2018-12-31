"""
    apnspy
    ~~~~~
    A tool for Apple Push Notification Service.
    It is based on token method.
    For more information, please check the Apple document
    https://developer.apple.com/library/archive/documentation/NetworkingInternet/Conceptual/RemoteNotificationsPG/CommunicatingwithAPNs.html#//apple_ref/doc/uid/TP40008194-CH11-SW1
"""

# standard module
import time
import json
import re
# 3rd party module
import jwt
from hyper import HTTP20Connection

class APNs(object):
    """
    """

    def __init__(self, sandbox=True, config_file=None):
        super(APNs, self).__init__()

        self.__algorithm = 'ES256'
        self.__init_time = time.time()
        with open(config_file) as cfg:
            input_str = re.sub(r'\\\n', '', cfg.read())
            input_str = re.sub(r'//.*\n', '\n', input_str)
            data = json.loads(input_str)
            self.__team_id = data["team_id"]
            self.__kid = data["apns_key_id"]
            self.__app_id = data["app_id"]
            self.__key_file = data["key_file"]

        with open(self.__key_file) as f:
            self.__secret = f.read()
        self.__token = jwt.encode({
                                   'iss': self.__team_id,
                                   'iat': self.__init_time
                                 },
                                 self.__secret,
                                 algorithm=self.__algorithm,
                                 headers={
                                   'alg': self.__algorithm,
                                   'kid': self.__kid
                                })

        if sandbox:
            self.__apns_server = 'api.development.push.apple.com:443'
        else:
            self.__apns_server = 'api.push.apple.com:443'
        self.__connect = HTTP20Connection(self.__apns_server, force_proto='h2')

    def send(self, message, sound, badges, payload=None, callback_func=None, device_token=None, content_available=False):
        """
        """
        if device_token is None:
            print 'Please provide the device token.'
            return
        path = '/3/device/{0}'.format(device_token)
        request_headers = {
            'apns-expiration': '0',
            'apns-priority': '10',
            'apns-topic': self.__app_id,
            'authorization': 'bearer {0}'.format(self.__token.decode('ascii'))
        }
        if content_available:
            content = 1
        else:
            content = 0
        payload_data = {
            'aps': {
                'alert' : message,
                'sound' : sound,
                'badge' : badges,
                'content-available': content
            }
        }

        if payload is not None:
            payload_data = payload
        body = json.dumps(payload_data).encode('utf-8')
        self.__connect.request(
            'POST',
            path,
            body=body,
            headers=request_headers
        )

        # https://github.com/genesluder/python-apns/pull/3
        # http://www.ehowstuff.com/how-to-install-and-update-openssl-on-centos-6-centos-7/
        resp = self.__connect.get_response()

        if callback_func == None:
            print(resp.status)
            print(resp.read())
        else:
            callback_func(resp, device_token)
