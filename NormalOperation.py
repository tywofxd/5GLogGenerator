import subprocess
import time
import os
from datetime import datetime, timedelta
chart_5g_dir = '/home/osboxes/towards5gs-helm/charts/free5gc'
helm_5g_release_name = 'free5gc'
pod_5g_name_list = ['amf', 'ausf', 'nrf', 'nssf', 'pcf', 'smf', 'udm', 'udr', 'upf', 'webui', 'mongodb']

gnb_script_dir = '/home/osboxes/5GLogGenerator/gnb.py'
ue_script_dir = '/home/osboxes/5GLogGenerator/run.py'
ue_command_wait_minutes = 4

current_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
time_record_file = './trace_normal/%s_normal_operation_time_records.txt' % current_time

def check_helm_release():
    '''判断当前cluster中是否安装了5g的helm release'''
    cmd = 'helm list -n default'
    output = subprocess.check_output(cmd, shell=True).decode()
    lines = output.split('\n')[1:]  # first line is the header

    for line in lines:
        if not line.strip():  # ignore empty lines
            continue

        name = line.split()[0]  # first column is name
        if name == helm_5g_release_name:
            return True

    return False

def check_pods_running():
    '''判断当前5g NF pods们是否都处于running状态'''
    cmd = 'kubectl get pods -n default'
    output = subprocess.check_output(cmd, shell=True).decode()
    lines = output.split('\n')[1:]  # first line is the header
    pods_checked = []

    for line in lines:
        if not line.strip():  # ignore empty lines
            continue

        name, status = line.split()[0], line.split()[2]  # first column is name, third is status
        if any(pod in name for pod in pod_5g_name_list):
            pods_checked.append([pod for pod in pod_5g_name_list if pod in name][0])
            if status.lower() != 'running':
                return False
    if set(pods_checked) != set(pod_5g_name_list):
        # Not all 5G NF pods are present in the Kubernetes cluster.
        return False

    return True

def check_pods_absence():
    '''判断当前5g NF pods们是否都停止了'''
    cmd = 'kubectl get pods -n default'
    output = subprocess.check_output(cmd, shell=True).decode()
    lines = output.split('\n')[1:]  # first line is the header

    for line in lines:
        if not line.strip():  # ignore empty lines
            continue

        name = line.split()[0]  # first column is name
        if any(pod in name for pod in pod_5g_name_list):
            return False

    return True

def one_round_normal():
    '''一次收集正常数据的全过程'''
    # 使用helm部署5G核心网
    helm_deploy_cmd = 'helm install %s %s' % (helm_5g_release_name,chart_5g_dir)
    os.system(helm_deploy_cmd)
    # 如果NFs没有全部是running状态，就一直等待
    while not check_pods_running():
        time.sleep(5)
    # 等NF全部running了，记录本次正常交互的开始时间戳
    start_timestamp_str = datetime.now().isoformat()
    with open(time_record_file, 'a') as f:
        f.write(start_timestamp_str + ' ')
    # 开始本次UE和核心网的交互，并等待交互结束
    run_ue_cmd = 'python3.8 %s --net5gc %s --ue 1 --sec 1000000' %(ue_script_dir, helm_5g_release_name)
    os.system(run_ue_cmd)
    # 记录结束时间，正常的结束时间应该是UE发起最后一次正常执行命令的时间
    end_timestamp_str = (datetime.now() - timedelta(minutes=ue_command_wait_minutes)).isoformat()
    with open(time_record_file, 'a') as f:
        f.write(end_timestamp_str + '\n')
    # 终止核心网
    helm_uninstall_cmd = 'helm uninstall %s ' % helm_5g_release_name
    os.system(helm_uninstall_cmd)
    time.sleep(1)


if __name__ == "__main__":
    exp_n = 1
    if check_helm_release():
        print("please uninstall the 5G core")
    else:
        # 启动gnb
        run_gnb_cmd = 'python3.8 %s &' % gnb_script_dir
        gnb_process = subprocess.Popen(run_gnb_cmd, shell=True)
        while exp_n<101:
            one_round_normal()
            exp_n += 1
            # 如果pods没有都停止，就等
            while not check_pods_absence():
                time.sleep(5)
        subprocess.Popen(["kill", "-9", str(gnb_process.pid)])
        
