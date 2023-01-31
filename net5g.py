import os
import re
import abc
import time
import shutil
import random
from tqdm import tqdm
import threading

UERANSIM_dir = "/home/osboxes/UERANSIM/build/"

class Net5GC():
    def __init__(self, ne5gc_type):
        self.commands = []
        self.commands_id = []
        self.current_file = ""
        self.simcard_data = ""
        self.ne5gc_type =ne5gc_type
        self.log_dir = "./logs"
        self.config_dir = "./config"
        self.config_filename_format = "*-ue-imsi-*.yaml"
        self.ueId_prefix = ""
        pass
    
    def _ck_mkdirs(self):
        """Check and make directories"""
        if os.path.exists(self.log_dir):
            shutil.rmtree(self.log_dir)
        os.makedirs(self.log_dir)
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)

    def generateUEConfigFile(self, ueId,):
        ueId = self._prefix_ueId(ueId)
        filename = "%s-ue-%s.yaml" % (self.ne5gc_type, ueId)
        os.system("cp ./%s-ue-template.yaml %s/%s" % (self.ne5gc_type, self.config_dir, filename))
        os.system("sed -i 's/imsi-208930000000003/%s/g' %s/%s" % (ueId, self.config_dir, filename))
    
    def _prefix_ueId(self, ueId):
        return self.ueId_prefix + ueId

    def _retrieveCurrentUeIMSI(self):
        currentUeIMSI = 1
        with open(self.current_file, "r") as reader:
            currentUeIMSI = int(reader.readline())
        return currentUeIMSI
    
    def _writeCurrentUeIMSI(self, currentUeIMSI):
        with open(self.current_file, "w") as writer:
            writer.write(str(currentUeIMSI))
    
    @abc.abstractmethod
    def sendSIMCardMsg(self, numbers, currentUeIMSI):
        print("Net5GC abstract method!")
        return

    def recordSIMCard(self, numbers=2):
        currentUeIMSI = self._retrieveCurrentUeIMSI()
        self.sendSIMCardMsg(numbers, currentUeIMSI)
        self._writeCurrentUeIMSI(currentUeIMSI + numbers)

    def _randomChoicePDUId(self, ueId):
        pdus = os.popen("%snr-cli -e ps-list %s | grep 'PDU Session'" %(UERANSIM_dir, ueId)).read()
        # pdu_count = self._couterPDU(ueId)

        pdus = pdus.split("\n")[:-1]
        if len(pdus) < 1:
            return None
        pduIds = []
        
        for pdu in pdus:
            pduId = re.search("\d+", pdu).group()
            pduId = int(pduId)
            pduIds.append(pduId)
        selected_pduId = random.choice(pduIds)
        return selected_pduId

    def _couterPDU(self, ueId):
        pdus = os.popen(UERANSIM_dir + "nr-cli -e ps-list " + ueId).read()
        return pdus.count("PDU Session")

    def randomCommands(self, ueId, over):
        while True:
            if time.perf_counter() >= over:
                break
            command_id = random.choice(self.commands_id)
            command = self.commands[command_id]
            pduNum_before = None
            if command == "ps-release":
                pduId = self._randomChoicePDUId(ueId)
                if pduId is None:
                    continue
                command = command + " " + str(pduId);
                pduNum_before = self._couterPDU(ueId)
            execute_cmd = "%snr-cli -e '%s' %s" % (UERANSIM_dir, command, ueId)
            print("LOG:  execute %s" % execute_cmd)
            os.system(execute_cmd)
            timer = 0
            flag = True
            while(True):
                if self._isCommandFinish(command_id, ueId, pduNum_before):
                    break
                # 2 minutes, 2*12*5 seconds
                # wait 2 minutes for the command to finish; if it cannot finish, deregister it, and wait another 2 minutes to throw the runtimeError.
                if timer >= 2*12:
                    if not flag:
                        raise RuntimeError("Maybe there are some problem in your core network, please check it.")
                    self._deregisterByUeId(ueId)
                    command_id = self.commands.index("deregister normal")
                    timer = 0
                    flag = False
                    
                time.sleep(5)
                timer += 1
    
    
    def _isCommandFinish(self, command_id, ueId, pduNum_before=None):
        """Whether a command execute sucessfully."""
        if command_id == 2 and pduNum_before > 1:
            # ps_release (more than one ps)
            return self._couterPDU(ueId) +1 == pduNum_before
        elif command_id in self.commands_id:
            # ps_release (only one ps), ps_release_all, deregister, ps_estabish
            # if suceeded, ue's log contains "TUN interface" 
            ueId_digit = re.search("\d+", ueId).group()
            log = os.popen("tail -n 1 %s/%s.out| grep 'TUN interface'" % (self.log_dir, ueId_digit)).read()
            return len(log.split('\n')) > 1
        else:
            raise RuntimeError("Command_id out of index.")
            

    def _deregisterByUeId(delf, ueId):
        os.system("%snr-cli -e 'deregister normal' %s" %  (UERANSIM_dir, ueId))


    def _terminateAllUE(self):
        query_ue_processes = os.popen("ps -a | grep nr-ue").read()
        ue_processes = query_ue_processes.split("\n")
        
        if len(ue_processes[:-1]) == 0:
            return
        print("Terminating all UEs process. if it dosen't stop for a while, please press Ctrl + C twice. About 10 seconds.")
        for ue_process in tqdm(ue_processes[:-1], desc='Terminating UEs: '):
            #ue_process.bar.set_description("Teminate UEs: ")
            items = ue_process.strip().split(" ")
            if len(items) > 0:
                # print("kill -9 " + items[0])
                os.system("kill -9 " + items[0])
        time.sleep(2)

    def startUEs(self, numbers=1):
        """Start UEs and save their logs"""
        self._terminateAllUE()
        files = os.listdir(self.config_dir)
        files = random.sample(files, numbers)
        # print(files)
        for file in tqdm(files, desc='Starting UEs: '):
            #file.bar.set_description("Start UEs: ")
            log_file = file.split('.')[0].split('-')[3]
            os.system("nohup %snr-ue -c %s/%s > %s/%s.out 2>&1 &" % (UERANSIM_dir, self.config_dir, file, self.log_dir, log_file))
            time.sleep(2)
    

    def generate(self, sec):
        query_ueIds = os.popen(UERANSIM_dir + "nr-cli -d | grep imsi").read()
        ueIds = query_ueIds.split("\n")
        ueIds = ueIds[:-1]
        print(ueIds)
        start = time.perf_counter()
        ueThreads = []
        for ueId in ueIds:
            try:
                thread = threading.Thread(target=self.randomCommands, args=(ueId, start + sec,))
                ueThreads.append(thread)
                thread.start()
            except:
                print("Error: unable to start thread")

        for thread in ueThreads:
            thread.join()

        self._terminateAllUE()
