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
from functools import wraps
# 3rd party module
import jwt
from hyper import HTTP20Connection


class APNs(object):
    """
    Base constuctor to generate an APNs object
        :param sandbox: For development, set True. For production, set False
        :param config_file: the path to the config file
    """

    def __init__(self, config_file=None):
        super(APNs, self).__init__()

        self.__algorithm = 'ES256'
        self.__init_time = time.time()
        with open(config_file) as cfg:
            input_str = re.sub(r'\\\n', '', cfg.read())
            input_str = re.sub(r'//.*\n', '\n', input_str)
            data = json.loads(input_str)
            self.__sandbox = data["sandbox"]
            self.__team_id = data["team_id"]
            self.__kid = data["apns_key_id"]
            self.__app_id = data["app_id"]
            self.__key_file = data["key_file"]

        with open(self.__key_file) as f:
            self.__secret = f.read()
        self.__token = self.getToken()

        if self.__sandbox:
            self.__apns_server = 'api.development.push.apple.com:443'
        else:
            self.__apns_server = 'api.push.apple.com:443'
        self.__connect = HTTP20Connection(self.__apns_server, force_proto='h2')

    def getToken(self):
        """
        Generate a new JWT token. If the timestamp for token issue is not within
        the last hour, APNs rejects subsequent push messages, returning
        an ExpiredProviderToken (403) error.
        """
        return jwt.encode(
                {
                    'iss': self.__team_id,
                    'iat': self.__init_time
                },
                self.__secret,
                algorithm=self.__algorithm,
                headers={
                    'alg': self.__algorithm,
                    'kid': self.__kid
                }
                )

    def checkConnection(function):
        """
        Check the HTTP2 connection.
        If the client connects to APNs more than an hour,
        reset the connection

        :return: a JWT token
        :rtype: a str type
        """
        @wraps(function)
        def decorator(*args, **kwargs):

            if time.time() - args[0].__init_time > 3600:
                args[0].__init_time = time.time()
                args[0].__token = args[0].getToken()
                args[0].__connect = HTTP20Connection(args[0].__apns_server, force_proto='h2')
            return function(*args, **kwargs)

        return decorator

    @checkConnection
    def send(self, message=None, sound=None, badges=None, payload=None,
             callback_func=None, device_token=None, 
             content_available=False, mutable_content = False):
        """
        send a message to one device
            :param message: the mssage will send to devices
            :param sound: the notification sound
            :param badges: the number of badges shows on devices
            :param payload: a dictionary defined by developers. Please check Apple developer webpage
                https://developer.apple.com/library/archive/documentation/NetworkingInternet/Conceptual/RemoteNotificationsPG/CreatingtheNotificationPayload.html#//apple_ref/doc/uid/TP40008194-CH10-SW1
            :param callback_func: the function will run after receiving the web response
            :param device_token: the target device token generated by Apple Push Notification Service
            :param content_available: if True,
                                      devices can run the background process.
            :param mutable_content: if True,
                                      devices can run the notification extension service.
            :type message: str
            :type sound: str
            :type badges: int
            :type payload: dict
            :type callback_func: function
            :type device_token: str
            :type content_available: bool
            :type mutable_content: bool
        """
        if device_token is None:
            print('Please provide the device token.')
            return
        path = '/3/device/{0}'.format(device_token)
        request_headers = {
            'apns-expiration': '0',
            'apns-priority': '10',
            'apns-topic': self.__app_id,
            'authorization': 'bearer {0}'.format(self.__token.decode('ascii'))
        }
        
        payload_data = { 'aps': {}}

        # setup a basic payload
        if message is not None:
            payload_data['aps']['alert'] = message
        if sound is not None:
            payload_data['aps']['sound'] = sound
        if badges is not None:
            payload_data['aps']['badge'] = badges
        if content_available == True:
            payload_data['aps']['content-available'] = 1
        if mutable_content == True:
            payload_data['aps']['mutable-content'] = 1

        # setup the custome payload and discard the basic payload
        if payload is not None:
            payload_data = payload
        body = json.dumps(payload_data).encode('utf-8')

        streamID = self.__connect.request(
            'POST',
            path,
            body=body,
            headers=request_headers
        )

        resp = self.__connect.get_response(streamID)

        if callback_func is None:
            return resp
        else:
            callback_func(resp, device_token)
