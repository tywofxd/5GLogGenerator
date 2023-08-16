import time
import subprocess
import os
from tqdm import tqdm
import random
from datetime import datetime

UERANSIM_dir = "/home/osboxes/UERANSIM/build/"
UE_config_file = "/home/osboxes/5GLogGenerator/config/free5gc/free5gc-ue-imsi-208930000000004.yaml"

UE_commands = [
    'ps-release-all',
    'deregister normal',
    'ps-establish IPv4 --sst 1 --sd 66051 --dnn internet'
]

faults = [
        # network-delay
        'amf-network-delay', 'ausf-network-delay', 'nrf-network-delay', 'nssf-network-delay', 'pcf-network-delay',
        'smf-network-delay', 'udm-network-delay', 'udr-network-delay',

        # network-loss
        'amf-network-loss', 'ausf-network-loss', 'nrf-network-loss', 'nssf-network-loss', 'pcf-network-loss',
        'smf-network-loss', 'udm-network-loss', 'udr-network-loss',

        # network-corrupt
        'amf-network-corrupt', 'ausf-network-corrupt', 'nrf-network-corrupt', 'nssf-network-corrupt', 'pcf-network-corrupt',
        'smf-network-corrupt', 'udm-network-corrupt', 'udr-network-corrupt',

        # pod-failure
        'amf-pod-failure', 'ausf-pod-failure', 'nrf-pod-failure', 'nssf-pod-failure', 'pcf-pod-failure',
        'smf-pod-failure', 'udm-pod-failure', 'udr-pod-failure',

        # cpu-stress
        'amf-cpu-stress', 'ausf-cpu-stress', 'nrf-cpu-stress', 'nssf-cpu-stress', 'pcf-cpu-stress',
        'smf-cpu-stress', 'udm-cpu-stress', 'udr-cpu-stress',

        # memory-stress
        'amf-memory-stress', 'ausf-memory-stress', 'nrf-memory-stress', 'nssf-memory-stress', 'pcf-memory-stress',
        'smf-memory-stress', 'udm-memory-stress', 'udr-memory-stress'
    ]

chaos_paths = {
    'amf-network-delay': '/home/osboxes/chaosmesh/network_delay/amf_network_delay.yaml',
    'ausf-network-delay': '/home/osboxes/chaosmesh/network_delay/ausf_network_delay.yaml',
    'nrf-network-delay': '/home/osboxes/chaosmesh/network_delay/nrf_network_delay.yaml',
    'nssf-network-delay': '/home/osboxes/chaosmesh/network_delay/nssf_network_delay.yaml',
    'pcf-network-delay': '/home/osboxes/chaosmesh/network_delay/pcf_network_delay.yaml',
    'smf-network-delay': '/home/osboxes/chaosmesh/network_delay/smf_network_delay.yaml',
    'udm-network-delay': '/home/osboxes/chaosmesh/network_delay/udm_network_delay.yaml',
    'udr-network-delay': '/home/osboxes/chaosmesh/network_delay/udr_network_delay.yaml',

    'amf-network-loss': '/home/osboxes/chaosmesh/network_loss/amf_network_loss.yaml',
    'ausf-network-loss': '/home/osboxes/chaosmesh/network_loss/ausf_network_loss.yaml',
    'nrf-network-loss': '/home/osboxes/chaosmesh/network_loss/nrf_network_loss.yaml',
    'nssf-network-loss': '/home/osboxes/chaosmesh/network_loss/nssf_network_loss.yaml',
    'pcf-network-loss': '/home/osboxes/chaosmesh/network_loss/pcf_network_loss.yaml',
    'smf-network-loss': '/home/osboxes/chaosmesh/network_loss/smf_network_loss.yaml',
    'udm-network-loss': '/home/osboxes/chaosmesh/network_loss/udm_network_loss.yaml',
    'udr-network-loss': '/home/osboxes/chaosmesh/network_loss/udr_network_loss.yaml',

    'amf-network-corrupt': '/home/osboxes/chaosmesh/network_corrupt/amf_network_corrupt.yaml',
    'ausf-network-corrupt': '/home/osboxes/chaosmesh/network_corrupt/ausf_network_corrupt.yaml',
    'nrf-network-corrupt': '/home/osboxes/chaosmesh/network_corrupt/nrf_network_corrupt.yaml',
    'nssf-network-corrupt': '/home/osboxes/chaosmesh/network_corrupt/nssf_network_corrupt.yaml',
    'pcf-network-corrupt': '/home/osboxes/chaosmesh/network_corrupt/pcf_network_corrupt.yaml',
    'smf-network-corrupt': '/home/osboxes/chaosmesh/network_corrupt/smf_network_corrupt.yaml',
    'udm-network-corrupt': '/home/osboxes/chaosmesh/network_corrupt/udm_network_corrupt.yaml',
    'udr-network-corrupt': '/home/osboxes/chaosmesh/network_corrupt/udr_network_corrupt.yaml',

    'amf-pod-failure': '/home/osboxes/chaosmesh/pod_failure/amf_pod_failure.yaml',
    'ausf-pod-failure': '/home/osboxes/chaosmesh/pod_failure/ausf_pod_failure.yaml',
    'nrf-pod-failure': '/home/osboxes/chaosmesh/pod_failure/nrf_pod_failure.yaml',
    'nssf-pod-failure': '/home/osboxes/chaosmesh/pod_failure/nssf_pod_failure.yaml',
    'pcf-pod-failure': '/home/osboxes/chaosmesh/pod_failure/pcf_pod_failure.yaml',
    'smf-pod-failure': '/home/osboxes/chaosmesh/pod_failure/smf_pod_failure.yaml',
    'udm-pod-failure': '/home/osboxes/chaosmesh/pod_failure/udm_pod_failure.yaml',
    'udr-pod-failure': '/home/osboxes/chaosmesh/pod_failure/udr_pod_failure.yaml',

    'amf-cpu-stress': '/home/osboxes/chaosmesh/cpu_stress/amf_cpu_stress.yaml',
    'ausf-cpu-stress': '/home/osboxes/chaosmesh/cpu_stress/ausf_cpu_stress.yaml',
    'nrf-cpu-stress': '/home/osboxes/chaosmesh/cpu_stress/nrf_cpu_stress.yaml',
    'nssf-cpu-stress': '/home/osboxes/chaosmesh/cpu_stress/nssf_cpu_stress.yaml',
    'pcf-cpu-stress': '/home/osboxes/chaosmesh/cpu_stress/pcf_cpu_stress.yaml',
    'smf-cpu-stress': '/home/osboxes/chaosmesh/cpu_stress/smf_cpu_stress.yaml',
    'udm-cpu-stress': '/home/osboxes/chaosmesh/cpu_stress/udm_cpu_stress.yaml',
    'udr-cpu-stress': '/home/osboxes/chaosmesh/cpu_stress/udr_cpu_stress.yaml',

    'amf-memory-stress': '/home/osboxes/chaosmesh/memory_stress/amf_memory_stress.yaml',
    'ausf-memory-stress': '/home/osboxes/chaosmesh/memory_stress/ausf_memory_stress.yaml',
    'nrf-memory-stress': '/home/osboxes/chaosmesh/memory_stress/nrf_memory_stress.yaml',
    'nssf-memory-stress': '/home/osboxes/chaosmesh/memory_stress/nssf_memory_stress.yaml',
    'pcf-memory-stress': '/home/osboxes/chaosmesh/memory_stress/pcf_memory_stress.yaml',
    'smf-memory-stress': '/home/osboxes/chaosmesh/memory_stress/smf_memory_stress.yaml',
    'udm-memory-stress': '/home/osboxes/chaosmesh/memory_stress/udm_memory_stress.yaml',
    'udr-memory-stress': '/home/osboxes/chaosmesh/memory_stress/udr_memory_stress.yaml',
}

def apply_chaos(file_path):
    command = ['kubectl', 'apply', '-f', file_path]
    result = subprocess.run(command, check=True, text=True, capture_output=True)
    if 'created' in result.stdout:
        return True
    else:
        return False

def delete_chaos(file_path):
    command = ['kubectl', 'delete', '-f', file_path]
    result = subprocess.run(command, check=True, text=True, capture_output=True)
    if 'deleted' in result.stdout:
        return True
    else:
        return False

def terminateUE():
    query_ue_processes = os.popen("ps -a | grep nr-ue").read()
    ue_processes = query_ue_processes.split("\n")
    
    if len(ue_processes[:-1]) == 0:
        return
    for ue_process in tqdm(ue_processes[:-1], desc='Terminating UE: '):
        #ue_process.bar.set_description("Teminate UEs: ")
        items = ue_process.strip().split(" ")
        if len(items) > 0:
            # print("kill -9 " + items[0])
            os.system("kill -9 " + items[0])
    time.sleep(2)

def startUE():
    """Start UE"""
    # 异步执行UE的启动命令
    start_ue_command = '%snr-ue -c %s' % (UERANSIM_dir, UE_config_file)
    subprocess.Popen(start_ue_command, shell=True)
    time.sleep(10)
    query_ueId = os.popen(UERANSIM_dir + "nr-cli -d | grep imsi").read()
    ueId = query_ueId.split("\n")[0]
    # 让该UE随机执行一个命令
    ue_random_command = "%snr-cli -e '%s' %s" % (UERANSIM_dir, random.choice[UE_commands], ueId)
    subprocess.Popen(ue_random_command, shell=True)
    time.sleep(10)

def chaos_fault_injection():
    current_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    chaos_injection_time_file = './%s_chaos_injection_time_records.txt' % current_time
    # 针对每种fault进行几次实验
    injection_num = 100
    for fault in faults:
        for exp_idx in range(len(injection_num)):
            print("fault %s; exp index %d;" %(fault, exp_idx))
            if apply_chaos(chaos_paths[fault]):
                # 记录故障注入开始时间
                start_timestamp_str = datetime.now().isoformat()
                startUE()
                # 记录故障结束时间
                end_timestamp_str = datetime.now().isoformat()
                # 停止UE
                terminateUE()
                # 恢复故障
                if delete_chaos(chaos_paths[fault]):
                    with open(chaos_injection_time_file, 'a') as f:
                        f.write(  "%s %d %s %s\n" %(fault, exp_idx, start_timestamp_str, end_timestamp_str))
                    # 再修复一段时间
                    time.sleep(5)
                else:
                    raise RuntimeError('%s chaos delete failure' % fault)

            else:
                raise RuntimeError('%s chaos inject failure' % fault)
            


