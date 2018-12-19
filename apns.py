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


ALGORITHM = 'ES256'

APNS_KEY_ID = '4G6GL7T4PV'

# http://disq.us/p/1ecxfqv:
# CMD: fold -w 64 APNsAuthKey_my_id.p8 > certs/APNsAuthKey_my_id_fold.p8
APNS_AUTH_KEY = 'AuthKey_4G6GL7T4PV.p8'

TEAM_ID = '2435JUVQAS'
BUNDLE_ID = 'com.iamhomebody.push'

PUSH_ID = 'B102AAB758F39F1EEF9DBCC1711C7679FD61E409A749D55F9180D1E7AAB79980'

class check_connection(object):
    """docstring for check_connection"""
    def __init__(self, currentTime, connect):
        super(check_connection, self).__init__()
        self.currentTime = currentTime
        self.connect = connect

    def __call__(self, f):
        print 'inside check_connection __call__'
        def wrapper(*args, **kwargs):
            print self.currentTime
            if self.connect is not None:
                if time.time() - self.currentTime > 3600:
                    print time.time() - self.currentTime
                    self.connect.connect()
            f(*args, **kwargs)
        return wrapper

class APNs(object):
    """
    """
    apns_connect = None
    apns_time = None

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
        APNs.apns_connect = HTTP20Connection(self.__apns_server, force_proto='h2')

    # @check_connection(apns_time, apns_connect)
    def send(self, message, sound, badges, device_token=None, content_available=False):
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
        payload = json.dumps(payload_data).encode('utf-8')
        APNs.apns_connect.request(
            'POST',
            path,
            body=payload,
            headers=request_headers
        )

        # https://github.com/genesluder/python-apns/pull/3
        # http://www.ehowstuff.com/how-to-install-and-update-openssl-on-centos-6-centos-7/
        resp = APNs.apns_connect.get_response()
        print(resp.status)
        print(resp.read())


apns = APNs(sandbox=True, config_file="myconfig.json")
# apns.send('This is a test 2', 'default', 2, device_token=PUSH_ID, content_available=True)
while True:
    message = raw_input('Enter the message: ')
    if message == 'q' or message == 'exit':
        break
    print 'message: {}'.format(message)
    apns.send(message, 'default', 1, device_token=PUSH_ID, content_available=True)
# apns.send('This is a test 2', 'default', 2, device_token=PUSH_ID, content_available=True)
# # Send our request
# conn.request(
#     'POST',
#     path,
#     payload,
#     headers=request_headers
# )


# f = open(APNS_AUTH_KEY)
# secret = f.read()

# token = jwt.encode(
#     {
#         'iss': TEAM_ID,
#         'iat': time.time()
#     },
#     secret,
#     algorithm= ALGORITHM,
#     headers={
#         'alg': ALGORITHM,
#         'kid': APNS_KEY_ID
#     }
# )

# path = '/3/device/{0}'.format(PUSH_ID)

# request_headers = {
#     'apns-expiration': '0',
#     'apns-priority': '10',
#     'apns-topic': BUNDLE_ID,
#     'authorization': 'bearer {0}'.format(token.decode('ascii'))
# }

# # Open a connection the APNS server

# # https://github.com/genesluder/python-apns/pull/3
# # https://github.com/genesluder/python-apns/pull/3/commits/0f543b773c25b1a1d817f5f681912ed3c9c2ca35

# # Development
# conn = HTTP20Connection('api.development.push.apple.com:443', force_proto='h2')

# # Production
# # conn = HTTP20Connection('api.push.apple.com:443', force_proto='h2')

# payload_data = {
#     'aps': {
#         'alert' : 'All your base are belong to us.',
#         # This is silent push
#         'sound' : '',
#         # Key to silent push
#         'content-available': 1
#     }
# }
# payload = json.dumps(payload_data).encode('utf-8')

# # Send our request
# conn.request(
#     'POST',
#     path,
#     payload,
#     headers=request_headers
# )

# # https://github.com/genesluder/python-apns/pull/3
# # http://www.ehowstuff.com/how-to-install-and-update-openssl-on-centos-6-centos-7/
# resp = conn.get_response()
# print(resp.status)
# print(resp.read())

# # If we are sending multiple requests, use the same connection
# # payload_data = {
# #     'aps': {
# #         'alert' : 'You have no chance to survive. Make your time.',
# #         'sound' : 'default',
# #         'badges' : 1,
# #         'content-available': 1
# #     }
# # }
# # payload = json.dumps(payload_data).encode('utf-8')

# # conn.request(
# #     'POST',
# #     path,
# #     payload,
# #     headers=request_headers
# # )

# # resp = conn.get_response()
# # print(resp.status)
# # print(resp.read())