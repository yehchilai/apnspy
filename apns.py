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
    def __init__(self, currentTime):
        super(check_connection, self).__init__()
        self.currentTime = currentTime

    def __call__(self, f):
        print 'inside check_connection __call__'
        def wrapper(*args, **kwargs):
            print 'check connection.......'
            f(*args, **kwargs)
        return wrapper

class APNs(object):
    """docstring for APNs"""
    def __init__(self, sandbox=True, team_id=None, apns_key_id=None, bundle_id=None, key_file=None):
        super(APNs, self).__init__()
        self._team_id = team_id
        self._kid = apns_key_id
        self._algorithm = 'ES256'
        self._init_time = time.time()
        with open(key_file) as f:
            self._secret = f.read()
        self._token = jwt.encode({
                                   'iss': self._team_id,
                                   'iat': self._init_time
                                 },
                                 self._secret,
                                 algorithm=self._algorithm,
                                 headers={
                                   'alg': self._algorithm,
                                   'kid': self._kid
                                })
        self._bundle_id = bundle_id
        if sandbox:
            self._apns_server = 'api.development.push.apple.com:443'
        else:
            self._apns_server = 'api.push.apple.com:443'
        self._connect = HTTP20Connection(self._apns_server, force_proto='h2')

    @check_connection(time.time())
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
            'apns-topic': self._bundle_id,
            'authorization': 'bearer {0}'.format(self._token.decode('ascii'))
        }
        if content_available:
            content = 1
        else:
            content = 0
        payload_data = {
            'aps': {
                'alert' : message,
                # This is silent push
                'sound' : sound,
                'badge' : badges,
                # Key to silent push
                'content-available': content
            }
        }
        payload = json.dumps(payload_data).encode('utf-8')
        self._connect.request(
            'POST',
            path,
            payload,
            headers=request_headers
        )

        # https://github.com/genesluder/python-apns/pull/3
        # http://www.ehowstuff.com/how-to-install-and-update-openssl-on-centos-6-centos-7/
        resp = self._connect.get_response()
        print(resp.status)
        print(resp.read())


apns = APNs(sandbox=True, team_id=TEAM_ID, apns_key_id=APNS_KEY_ID, bundle_id=BUNDLE_ID, key_file=APNS_AUTH_KEY)
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