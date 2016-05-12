import time
import datetime
from hashlib import md5
import urllib.request
import urllib.parse
import urllib.error
import json

class WakaLive():

    def __init__(self,userid,secretkey):
        self.apiurl = 'http://api.open.letvcloud.com/live/execute'
        self.userid = userid
        self.ver = '3.0'
        self.secretkey = secretkey

    def generateSign(self, params):
        sign = ''
        sorted_params = sorted(params.items())
        for k, v in sorted_params:
            sign += (str(k) + str(v))
        sign += self.secretkey
        return md5(sign.encode()).hexdigest()

    def generateTimeStamp(self):
        return int(time.time() * 1000)

    def generateRequest(self, extra_params, method_is_get=True):
        origin_params = {
            'ver': '3.0',
            'userid': self.userid,
            'timestamp': self.generateTimeStamp()
        }
        post_data = dict(origin_params, **extra_params)
        post_data['sign'] = self.generateSign(post_data)
        data = urllib.parse.urlencode(post_data)
        try:
            if method_is_get:
                rep = urllib.request.urlopen(self.apiurl+ '?' + data)
            else:
                data = data.encode('utf-8')
                rep = urllib.request.urlopen(self.apiurl,data = data)
        except urllib.error.HTTPError as e:
            print('Server Error:',e.code)
            return self.json_load(e.read().decode('utf-8'))
        except urllib.error.URLError as e:
            print('Request Error:',e.reason)
            return self.json_load(e.read().decode('utf-8'))
        else:
            return self.json_load(rep.read().decode('utf-8'))

    def json_load(self,result):
        if result:
            return json.loads(result)
        else:
            return None

    #码率类型，逗号分隔。由大到小排列。取值范围：13 标清；16 高清；19 超清；22 720P；25 1080P；99 原画
    def createLive(self, params):
        post_data = {
            'method': 'letv.cloudlive.activity.create',
            'activityName': params['activityName'],
            'startTime': time.strftime("%Y%m%d%H%M%S"),
            'endTime': time.strftime("%Y%m%d%H%M%S", time.localtime(time.time() + 2592000)),
            'description': params['description'],
            'liveNum': 1,
            'codeRateTypes': params['codeRateTypes'],
            'activityCategory': '999',
            'playMode': 0
        }
        return self.generateRequest(post_data, method_is_get=False)['activityId']

    def modifyLive(self, params):
        post_data = {
            'method': 'letv.cloudlive.activity.modify',
            'activityId' : params['activityId']
        }
        if 'activityName' in params:
            post_data['activityName'] = params['activityName']
        if 'description' in params:
            post_data['description'] = params['description']
        if 'codeRateTypes' in params:
            post_data['codeRateTypes'] = params['codeRateTypes']
        return self.generateRequest(post_data, method_is_get=False)

    def getPushUrl(self,aid):
        post_data = {
            'method': 'letv.cloudlive.activity.getPushUrl',
            'activityId' : aid
        }
        return self.generateRequest(post_data)['lives'][0]['pushUrl']

    def cancelLive(self,aid):
        params = {
            'method' : 'letv.cloudlive.activity.stop',
            'activityId' : aid
        }
        return self.generateRequest(extra_params=params,method_is_get=False)

    def queryLive(self, aid, livestatus=1):
        params = {
            'method' : 'letv.cloudlive.activity.search'
        }
        if 'activityId' is not None:
            params['activityId'] = aid
        elif livestatus:
            params['activityStatus'] = livestatus
        return self.generateRequest(extra_params=params)[0]
