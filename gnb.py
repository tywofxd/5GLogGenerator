from resources.ip import open5gsIP,gnbIP
from net5g import UERANSIM_dir
import os
import time 

gnb_log_dir = "./logs"

def gnb_config_init():
    filename = "./config/gnb/open5gs-gnb.yaml"
    os.system("sed -i 's/192.168.59.134/%s/g' %s" % (gnbIP, filename))
    os.system("sed -i 's/192.168.59.130/%s/g' %s" % (open5gsIP, filename))

def gnb_monitor():
    gnb_config_init()
    stop_gnb()
    while True:
        gnbId = parse_gnb_id()
        while len(gnbId) == 0:
            gnbId = start_gnb()
            print("gnbId:"+ gnbId +" started")
        # test the connection between gnb and AMF every 2 seconds
        amf_list = getAMFlist(gnbId)
        # print("gnbId:"+ gnbId +"; " + "amf-list: " + str(amf_list))
        gnb_restart_flag = False
        if sum(amf != '' for amf in amf_list) < 1:
            print("restarting gnb.")
            gnbId = restart_gnb()
            # judge whether the new started gnb can connect with AMF
            while not judge_AMF_connects():
                gnbId = restart_gnb()
            gnb_restart_flag = True
        if gnb_restart_flag:
            print("gnb has been restarted.")
            
        time.sleep(2)


def judge_AMF_connects():
    key_log = os.popen("head %s/gnb.out| grep 'NG Setup procedure is successful'" % gnb_log_dir ).read()
    return len(key_log.split('\n')) > 1


def parse_gnb_id():
    gnb_id_str = os.popen("%snr-cli -d | grep gnb" % UERANSIM_dir).read()
    gnb_ids = gnb_id_str.split("\n")
    return gnb_ids[0]


def restart_gnb():
    stop_gnb()
    gnbId = start_gnb()
    return gnbId


def start_gnb():
    config_file = "./config/gnb/open5gs-gnb.yaml"
    os.system("nohup %snr-gnb -c %s > %s/gnb.out 2>&1 &" % (UERANSIM_dir, config_file, gnb_log_dir))
    time.sleep(1)
    gnbId = parse_gnb_id()
    return gnbId

def getAMFlist(gnbId):
    amf_list_str = os.popen("%snr-cli -e amf-list %s" % (UERANSIM_dir, gnbId)).read()
    amf_list = amf_list_str.split("\n")
    return amf_list


def stop_gnb():
    processes_str = os.popen("ps -a | grep nr-gnb").read()
    processes = processes_str.split("\n")[:-1]
    for gnb_process in processes:
        process_id = gnb_process.strip().split(" ")[0]
        if len(process_id) > 0:
            os.system("kill -9 " + process_id)
    


if __name__ == '__main__':
    gnb_monitor()

