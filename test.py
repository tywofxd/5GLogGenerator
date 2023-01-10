import os
import time 

commands = [
    'ps-establish',
    'ps-list',
    'ps-release',
    'ps-release-all',
    'deregister normal',
    'ps-establish IPv4 --emergency',
    'ps-establish IPv4 --sst 1 --sd 66051 --dnn internet'
]


for i in range(10):
    os.system("/opt/module/UERANSIM/build/nr-cli -e 'deregister normal' imsi-208930000000103")
    print("/opt/module/UERANSIM/build/nr-cli -e 'deregister normal' imsi-208930000000103")
    time.sleep(30)