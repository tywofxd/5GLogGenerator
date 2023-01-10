
"""
http://192.168.59.130:3000/api/auth/login

Accept: application/json, text/plain, */*
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7
Connection: keep-alive
Content-Length: 38
Content-Type: application/json
Cookie: connect.sid=s%3ABdL602qURE4klNfQWTCsEdDJa9Ixg455.A6A14pKyhZsrdr2XDVT8ngBG5zT149Z9hGMdTl%2BFJEE
Host: 192.168.59.130:3000
Origin: http://192.168.59.130:3000
Referer: http://192.168.59.130:3000/
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36
X-CSRF-TOKEN: m9hHYbDSDFeFJBuD3gSDuPXowAAjh6nwOp9VQ=

http://192.168.59.130:3000/api/auth/session

http://192.168.59.130:3000/api/db/Subscriber
Accept: application/json, text/plain, */*
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjp7Il9pZCI6IjYzYjQ1OWYyMGIyODc1NmE3NGU1NzRlYiIsInVzZXJuYW1lIjoiYWRtaW4iLCJyb2xlcyI6WyJhZG1pbiJdfSwiaWF0IjoxNjcyNzYzOTE0fQ.fkdfuYVpHe6-DkYVCt7TwT2T3piIpIldwfwAss3mWjQ
Connection: keep-alive
Content-Length: 539
Content-Type: application/json
Cookie: connect.sid=s%3AVMOV0W5j_SxKudK6ptHVinyE2wyyWoZG.tQXdMS4uHEVLQraJXMZmp%2FFIA9puS5mR3f6pmUdqDkM
Host: 192.168.59.130:3000
Origin: http://192.168.59.130:3000
Referer: http://192.168.59.130:3000/
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36
X-CSRF-TOKEN: vqp9s7pPMmv7l/g7QkCCxqRIFIX0TJoPX+JUA=


{"imsi": "208930000000004","security": {"k": "465B5CE8 B199B49F AA5F0A2E E238A6BC","amf": "8000","op_type": 0,"op_value": "E8ED289D EBA952E4 283B54E8 8E6183CA","op": null,"opc": "E8ED289D EBA952E4 283B54E8 8E6183CA"},"ambr": {"downlink": {"value": 1,"unit": 3},"uplink": {"value": 1,"unit": 3}},"slice": [{"sst": 1,"default_indicator": true,"session": [{"name": "internet", "type": 3,"ambr": {"downlink": {"value": 1,"unit": 3},"uplink": {"value": 1,"unit": 3}},"qos": {"index": 9,"arp": {"priority_level": 8,"pre_emption_capability": 1,"pre_emption_vulnerability": 1}}}]}]}
"""

import requests
import json
import time 
import argparse
import os
from net5g import Net5GC
from resources.open5gsConfig import *




class Open5GS(Net5GC):
    def __init__(self):
        super(Open5GS, self).__init__("open5gs")
        self.commands = commands
        self.commands_id = commands_id
        self.current_file = "./current/open5gs_current.txt"
        self.log_dir = "./logs/open5gs"
        self.config_dir = "./config/open5gs"
        self.config_filename_format = "open5gs-ue-imsi-%s.yaml"
        self.ueId_prefix = "imsi-"
        self.csrf_url = csrf_url
        self.headers_ = headers_
        self.login_url = login_url
        self.login_data = login_data
        self.headers_post = headers_post
        self.simcard_data = data1
        self.session_url = session_url
        self.headers_hascookie = headers_hascookie
        self.subscriber_url = subscriber_url
        self.headers_auth = headers_auth
        self._ck_mkdirs()
        
    def sendSIMCardMsg(self, numbers, currentUeIMSI):
        """Set 5GC network information. For the sake of simplicity and readibility, it will never check the response status code. """
        session = requests.Session()
        csrf_resp = session.get(self.csrf_url, headers=self.headers_)
        csrf_data = json.loads(csrf_resp.text)
        csrf_token = csrf_data['csrfToken']
        self.headers_post['X-CSRF-TOKEN'] = csrf_token
        self.headers_post['Cookie'] = csrf_resp.headers['Set-Cookie']
        login_resp = session.post(self.login_url, data=self.login_data, headers=self.headers_post)
        self.headers_hascookie['Cookie'] = login_resp.headers['Set-Cookie']
        session_resp = session.get(self.session_url, headers=self.headers_hascookie)
        #print(session_resp.text)
        session_data = json.loads(session_resp.text)
        csrf_token = session_data['csrfToken']
        auth_token = session_data['authToken']
        self.headers_auth['X-CSRF-TOKEN'] = csrf_token
        self.headers_auth['Cookie'] = session_resp.headers['Set-Cookie']
        self.headers_auth['Authorization'] = self.headers_auth['Authorization'] + auth_token
        data = json.loads(self.simcard_data)
        for ueid in range(currentUeIMSI, currentUeIMSI + numbers):
            data['imsi'] = "20893" + '{:010d}'.format(ueid)
            self.generateUEConfigFile(data['imsi'])
            subscriber_resp = session.post(self.subscriber_url, headers=self.headers_auth, data=json.dumps(data))
            if subscriber_resp.status_code == 201:
                self.headers_auth['Cookie'] = subscriber_resp.headers['Set-Cookie']
                print("UE SIM Card %s record successfully!" % data['imsi'])
            else:
                print("UE SIM Card %s record unsuccessfully!" % data['imsi'])
            time.sleep(2)








