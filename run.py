import threading
import time
import argparse
import os
from free5gc import Free5GC
from open5gs import Open5GS

"""v1.0"""
# if __name__ == '__main__':
#     parser = argparse.ArgumentParser()
#     parser.add_argument("--sec", help="How long does it run, default 10s", type=int, default=10)
#     parser.add_argument("--ue", help="The number of ues, default 1", type=int)
#     parser.add_argument("--simcard", help="The number of SimCards, default 2", type=int)
    
#     args = parser.parse_args()
#     if args.simcard:
#         recordSIMCard(numbers=args.simcard)
#     if args.ue:
#         startUEs(args.ue)
    
#     query_ueIds = os.popen("/opt/module/UERANSIM/build/nr-cli -d | grep imsi").read()
#     ueIds = query_ueIds.split("\n")
#     ueIds = ueIds[:-1]
#     print(ueIds)


#     start = time.perf_counter()

#     for ueId in ueIds:
#         try:
#             thread = threading.Thread(target=randomCommands, args=(ueId, start + args.sec,))
#             thread.start()
#         except:
#             print("Error: unable to start thread")

#     while time.perf_counter() <= start + args.sec:
#         pass

#     terminateAllUE()


"""v2.0"""
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--sec", help="How long does it run, default 10s", type=int, default=10)
    parser.add_argument("--ue", help="The number of ues, default 1", type=int)
    parser.add_argument("--simcard", help="The number of SimCards, default 2", type=int)
    parser.add_argument("--net5gc", help="The type of 5g core network, 'free5gc' or 'open5gs', default free5gc", default="free5gc")
    # parser.add_argument("--sudo", help="Running in not-root user", default="free5gc")

    args = parser.parse_args()
    net5gc = None
    if args.net5gc == "open5gs":
        net5gc = Open5GS()
    elif args.net5gc == "free5gc":
        net5gc = Free5GC()
    else:
        raise RuntimeError("--net5gc Value ERROR: Only support 'open5gs' and 'free5gc' ")

    
    if args.simcard:
        net5gc.recordSIMCard(numbers=args.simcard)
    if args.ue:
        net5gc.startUEs(args.ue)
        net5gc.generate(args.sec)
