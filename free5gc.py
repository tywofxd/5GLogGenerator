"""
"""

import os
import requests
import json
import time
import random
from net5g import Net5GC
from requests import Response
from resources.free5gcConfig import *


class Free5GC(Net5GC):

    def __init__(self):
        super(Free5GC, self).__init__("free5gc")
        self.commands = commands
        self.commands_id = commands_id
        self.current_file = "./current/free5gc_current.txt"
        self.log_dir = "./logs/free5gc"
        self.config_dir = "./config/free5gc"
        self.config_filename_format = "free5gc-ue-%s.yaml"
        self.simcard_data = data1
        self.headers = headers
        self.url = url
        self._ck_mkdirs()
        pass

    def sendSIMCardMsg(self, numbers, currentUeIMSI):
        data = json.loads(self.simcard_data)

        # nssai = 0
        for ueid in range(currentUeIMSI, currentUeIMSI + numbers):
            data["ueId"] = "imsi-20893" + '{:010d}'.format(ueid)
            self.generateUEConfigFile(data["ueId"])
            # nssai2 = '{:06x}'.format(nssai)
            # nssai cloud be changed. If need, please cancel the anotation.
            # data["SessionManagementSubscriptionData"][0]["singleNssai"]["sd"] = nssai2
            # data["SessionManagementSubscriptionData"][1]["singleNssai"]["sd"] = nssai2
            url1 = url + data["ueId"] + "/" + data["plmnID"]
            print(url1)
            resp: Response = requests.post(
                url=url1, headers=self.headers, data=json.dumps(data))
            if resp.status_code == 201:
                print("UE SIM Card %s record successfully!" % data["ueId"])
            else:
                print("UE SIM Card %s record unsuccessfully!" % data["ueId"])
            # print(data["plmnID"])
            # print(data)
            time.sleep(2)
            # nssai +=1







