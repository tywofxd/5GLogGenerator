import threading
import time
import argparse
import os
from free5gc import recordSIMCard
from free5gc import startUEs
from free5gc import randomCommands
from free5gc import terminateAllUE


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--sec", help="How long does it run, default 10s", type=int, default=10)
    parser.add_argument("--ue", help="The number of ues, default 1", type=int)
    parser.add_argument("--simcard", help="The number of SimCards, default 2", type=int)
    
    args = parser.parse_args()
    if args.simcard:
        recordSIMCard(numbers=args.simcard)
    if args.ue:
        startUEs(args.ue)
    
    query_ueIds = os.popen("/opt/module/UERANSIM/build/nr-cli -d | grep imsi").read()
    ueIds = query_ueIds.split("\n")
    ueIds = ueIds[:-1]
    print(ueIds)


    start = time.perf_counter()

    for ueId in ueIds:
        try:
            thread = threading.Thread(target=randomCommands, args=(ueId, start + args.sec,))
            thread.start()
        except:
            print("Error: unable to start thread")

    while time.perf_counter() <= start + args.sec:
        pass

    terminateAllUE()
