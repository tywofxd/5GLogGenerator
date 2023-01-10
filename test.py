# from tqdm import tqdm 
# from time import sleep

# pbar = tqdm(["a", "b", "c", "d"])
# s = ""
# for char in pbar:
#     print(char)
#     s = s + char
#     pbar.set_description("Processing %s" % char)

# print(s)

import os

s = os.popen("/opt/module/UERANSIM/build/nr-cli -e 'ps-list' imsi-208930000000003 | grep 'PDU Session'").read()
print(len(s.split('\n')))