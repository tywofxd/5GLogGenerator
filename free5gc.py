"""
deregister <normal|disable-5g|switch-off|remove-sim>
ps-release <pdu-session-id>...

Usage:                                                                                                
  ps-establish <session-type> [options]                                                               
                                                                                                     
Examples:                                                                                            
  ps-establish IPv4 --sst 1 --sd 1 --dnn internet                                                 
  ps-establish IPv4 --emergency                                                                       
Options:                                                                                              
  --sst <value>    SST value of the PDU session                                                       
  --sd <value>     SD value of the PDU session
  -n, --dnn <apn>  DNN/APN value of the PDU session
  -e, --emergency  Request as an emergency session

ps-establish is invalid. Maybe there are some problems in 5G core network.

开发说明：该程序存在很多问题
1. 过度调用系统命令
2. 一些参数未使用配置文件存储
"""

import os
import requests
import json
import time
import random
from requests import Response
import argparse


commands = [
    'ps-establish',
    'ps-list',
    'ps-release',
    'ps-release-all',
    'deregister normal'
]

commands_id = [3, 4]


# /api/subscriber/imsi-208930000000001/20893
free5gcIP = "192.168.59.133"
headers = {
    "Host": free5gcIP + ":5000",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "X-Requested-With": "XMLHttpRequest",
    "Content-Type": "application/json;charset=utf-8",
    "Token": "admin",
    "Origin": "http://"+ free5gcIP +":5000",
    "Connection": "keep-alive",
    "Referer": "http://"+ free5gcIP +":5000"
}

url = "http://"+ free5gcIP +":5000/api/subscriber/"
data1 = '{"plmnID":"20893","ueId":"imsi-208930000077777","AuthenticationSubscription":{"authenticationManagementField":"8000","authenticationMethod":"5G_AKA","milenage":{"op":{"encryptionAlgorithm":0,"encryptionKey":0,"opValue":""}},"opc":{"encryptionAlgorithm":0,"encryptionKey":0,"opcValue":"8e27b6af0e692e750f32667a3b14605d"},"permanentKey":{"encryptionAlgorithm":0,"encryptionKey":0,"permanentKeyValue":"8baf473f2f8fd09487cccbd7097c6862"},"sequenceNumber":"16f3b3f70fc2"},"AccessAndMobilitySubscriptionData":{"gpsis":["msisdn-0900000000"],"nssai":{"defaultSingleNssais":[{"sst":1,"sd":"010203","isDefault":true},{"sst":1,"sd":"112233","isDefault":true}],"singleNssais":[]},"subscribedUeAmbr":{"downlink":"2 Gbps","uplink":"1 Gbps"}},"SessionManagementSubscriptionData":[{"singleNssai":{"sst":1,"sd":"010203"},"dnnConfigurations":{"internet":{"sscModes":{"defaultSscMode":"SSC_MODE_1","allowedSscModes":["SSC_MODE_2","SSC_MODE_3"]},"pduSessionTypes":{"defaultSessionType":"IPV4","allowedSessionTypes":["IPV4"]},"sessionAmbr":{"uplink":"200 Mbps","downlink":"100 Mbps"},"5gQosProfile":{"5qi":9,"arp":{"priorityLevel":8},"priorityLevel":8}},"internet2":{"sscModes":{"defaultSscMode":"SSC_MODE_1","allowedSscModes":["SSC_MODE_2","SSC_MODE_3"]},"pduSessionTypes":{"defaultSessionType":"IPV4","allowedSessionTypes":["IPV4"]},"sessionAmbr":{"uplink":"200 Mbps","downlink":"100 Mbps"},"5gQosProfile":{"5qi":9,"arp":{"priorityLevel":8},"priorityLevel":8}}}},{"singleNssai":{"sst":1,"sd":"112233"},"dnnConfigurations":{"internet":{"sscModes":{"defaultSscMode":"SSC_MODE_1","allowedSscModes":["SSC_MODE_2","SSC_MODE_3"]},"pduSessionTypes":{"defaultSessionType":"IPV4","allowedSessionTypes":["IPV4"]},"sessionAmbr":{"uplink":"200 Mbps","downlink":"100 Mbps"},"5gQosProfile":{"5qi":9,"arp":{"priorityLevel":8},"priorityLevel":8}},"internet2":{"sscModes":{"defaultSscMode":"SSC_MODE_1","allowedSscModes":["SSC_MODE_2","SSC_MODE_3"]},"pduSessionTypes":{"defaultSessionType":"IPV4","allowedSessionTypes":["IPV4"]},"sessionAmbr":{"uplink":"200 Mbps","downlink":"100 Mbps"},"5gQosProfile":{"5qi":9,"arp":{"priorityLevel":8},"priorityLevel":8}}}}],"SmfSelectionSubscriptionData":{"DnnInfosubscribedSnssaiInfos":{"01010203":{"dnnInfos":[{"dnn":"internet"}]},"01112233":{"dnnInfos":[{"dnn":"internet"}]}}},"AmPolicyData":{"subscCats":["free5gc"]},"SmPolicyData":{"smPolicySnssaiData":{"01010203":{"snssai":{"sst":1,"sd":"010203"},"smPolicyDnnData":{"internet":{"dnn":"internet"}}},"01112233":{"snssai":{"sst":1,"sd":"112233"},"smPolicyDnnData":{"internet":{"dnn":"internet"}}}}},"FlowRules":[]}'

def generateUEConfigFile(ueId):
    """"""
    filename = "free5g-ue-%s.yaml" % ueId
    os.system("cp ./free5gc-ue-template.yaml ./config/" + filename)
    os.system("sed -i 's/imsi-208930000000003/%s/g' ./config/%s" % (ueId, filename))

def retrieveCurrentUeIMSI():
    currentUeIMSI = 1
    with open("./current.txt", "r") as reader:
        currentUeIMSI = int(reader.readline())
    return currentUeIMSI

def writeCurrentUeIMSI(currentUeIMSI):
    with open("./current.txt", "w") as writer:
        writer.write(str(currentUeIMSI))

def recordSIMCard(numbers=20):
    data = json.loads(data1)

    # nssai = 0
    currentUeIMSI = retrieveCurrentUeIMSI()
    for ueid in range(currentUeIMSI, currentUeIMSI + numbers):
        data["ueId"] = "imsi-2089300000" + '{:05d}'.format(ueid)
        generateUEConfigFile(data["ueId"])
        # nssai2 = '{:06x}'.format(nssai)
        # 如果需要修改nssai取消注释，nssai设置可行性未验证
        # data["SessionManagementSubscriptionData"][0]["singleNssai"]["sd"] = nssai2
        # data["SessionManagementSubscriptionData"][1]["singleNssai"]["sd"] = nssai2
        url1 = url + data["ueId"] + "/" + data["plmnID"]
        print(url1)
        resp: Response = requests.post(
            url=url1, headers=headers, data=json.dumps(data))

        if resp.status_code == 201:
            print("UE SIM Card %s record successfully!" % data["ueId"])
        else:
            print("UE SIM Card %s record unsuccessfully!" % data["ueId"])
        # print(data["plmnID"])
        # print(data)
        
        time.sleep(10)
        # nssai +=1
    writeCurrentUeIMSI(currentUeIMSI + numbers)


def randomCommands(ueIds, numbers=100):
    for i in range(numbers):
        command_id = random.choice(commands_id)
        command = commands[command_id]
        ueId = random.choice(ueIds)
        print("LOG:  execute %s" % ("/opt/module/UERANSIM/build/nr-cli -e '%s' %s" % (command, ueId)))
        os.system("/opt/module/UERANSIM/build/nr-cli -e '%s' %s" % (command, ueId))
        time.sleep(3)
        if command_id == 4:
            time.sleep(10)


def terminateAllUE():
    query_ue_processes = os.popen("ps -a | grep nr-ue").read()
    ue_processes = query_ue_processes.split("\n")
    for ue_process in ue_processes[:-1]:
        items = ue_process.strip().split(" ")
        if len(items) > 0:
            print("kill -9 " + items[0])
            os.system("kill -9 " + items[0])
    time.sleep(2)


def startUEs(numbers=1):
    terminateAllUE()
    files = os.listdir("./config/")
    files = random.sample(files, numbers)
    
    for file in files:
        os.system("nohup /opt/module/UERANSIM/build/nr-ue -c ./config/%s &" % file)



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--cmd", help="The number of commands, default 1", type=int, default=1)
    parser.add_argument("--ue", help="The number of ues, default 1", type=int, default=1)
    parser.add_argument("--enable", action="store_true", help="Enable to generate Sim Cards", default=False)
    parser.add_argument("--startue", action="store_true", help="Enable to generate Sim Cards", default=True)
    parser.add_argument("--simcard", help="The number of ues, default 2", type=int, default=2)
    
    args = parser.parse_args()
    if args.enable:
        recordSIMCard(numbers=args.simcard)
    if args.startue:
        startUEs(args.ue)
    
    query_ueIds = os.popen("/opt/module/UERANSIM/build/nr-cli -d | grep imsi").read()
    ueIds = query_ueIds.split("\n")
    ueIds = ueIds[:-1]
    print(ueIds)
    randomCommands(ueIds, numbers=args.cmd)

