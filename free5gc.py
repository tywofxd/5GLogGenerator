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
from resources import commands
from resources import commands_id
from resources import free5gcIP
from resources import headers
from resources import url
from resources import data1

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
        data["ueId"] = "imsi-20893" + '{:010d}'.format(ueid)
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


def retrievePDUId(ueId):
    pdus = os.popen("/opt/module/UERANSIM/build/nr-cli -e ps-list " + ueId).read()
    pdu_count = pdus.count("PDU Session")
    pduId = random.randint(1, pdu_count + 1)
    return pduId


def randomCommands(ueId, over):
    while True:
        if time.perf_counter() >= over:
            break
        command_id = random.choice(commands_id)
        command = commands[command_id]
        if command == "ps-release":
            command = command + " " + str(retrievePDUId(ueId));
        print("LOG:  execute %s" % ("/opt/module/UERANSIM/build/nr-cli -e '%s' %s" % (command, ueId)))
        os.system("/opt/module/UERANSIM/build/nr-cli -e '%s' %s" % (command, ueId))
        time.sleep(5)
        if command == "deregister normal" or command == "ps-establish":
            time.sleep(5)


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



