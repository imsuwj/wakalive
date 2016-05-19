from hashlib import md5
import urllib.request
import urllib.parse
import urllib.error
import json


class LeanCloud():

    def __init__(self, appid, appkey):
        self.api_url = 'https://api.leancloud.cn/1.1/classes/_Conversation'
        self.app_id = appid
        self.app_key = appkey

    def createRoom(self, name):
        headers = {
            'X-LC-Id': self.app_id,
            'X-LC-Key': self.app_key,
            'Content-Type': 'application/json'
        }
        data = {
            'name': name,
            'tr': True
        }
        data = json.dumps(data).encode('utf-8')
        req = urllib.request.Request(self.api_url, data=data, headers=headers)
        try:
            rep = urllib.request.urlopen(req)
        except urllib.error.HTTPError as e:
            print('Server Error:', e.code)
            #return json.loads(e.read().decode('utf-8'))
        except urllib.error.URLError as e:
            print('Request Error:', e.reason)
            #return json.loads(e.read().decode('utf-8'))
        else:
            return json.loads(rep.read().decode('utf-8'))['objectId']
