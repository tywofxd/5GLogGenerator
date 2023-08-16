'''
构造脚本，循环模拟rouge NF不断产生恶意调用行为。
'''
from EvilNF import *
from datetime import datetime, timedelta
import os
import multiprocessing

chart_5g_dir = '/home/osboxes/towards5gs-helm/charts/free5gc'
helm_5g_release_name = 'free5gc'
pod_5g_name_list = ['amf', 'ausf', 'nrf', 'nssf', 'pcf', 'smf', 'udm', 'udr', 'upf', 'webui', 'mongodb']
emulated_NF_list = ['amf', 'nrf', 'nssf']


gnb_script_dir = '/home/osboxes/5GLogGenerator/gnb.py'
ue_script_dir = '/home/osboxes/5GLogGenerator/run.py'

current_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
time_record_file = './evil_behavior/%s_evil_NF_delete_time_records.txt' % current_time

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

def deploy_5g():
    # 使用helm部署5G核心网
    helm_deploy_cmd = 'helm install %s %s' % (helm_5g_release_name,chart_5g_dir)
    os.system(helm_deploy_cmd)
    # 如果NFs没有全部是running状态，就一直等待
    while not check_pods_running():
        time.sleep(5)
    print("5G CN has been deployed")

def uninstall_5g():
    # 终止核心网
    helm_uninstall_cmd = 'helm uninstall %s ' % helm_5g_release_name
    os.system(helm_uninstall_cmd)
    time.sleep(1)
    # 如果pods没有都停止，就等
    while not check_pods_absence():
        time.sleep(5)
    print("5G CN has been uninstalled")

def execut_ue():
    run_ue_cmd = 'python3.8 %s --net5gc %s --ue 1 --sec 20' %(ue_script_dir, helm_5g_release_name)
    result = subprocess.run(run_ue_cmd, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(result.stdout)  # 打印标准输出
    if result.returncode != 0:
        if "RuntimeError" in result.stderr.lower():
            return False
    if result.stdout.count('LOG:') >= 2:
        return True
    return False
    

if __name__ == "__main__":
    # 若5g pods没部署好，需部署
    if not check_pods_running():
        print("5G is not deployed, begin deploying")
        deploy_5g()
    else:
        # 启动gnb
        run_gnb_cmd = 'python3.8 %s &' % gnb_script_dir
        gnb_process = subprocess.Popen(run_gnb_cmd, shell=True)
        exp_num = 50
        # 遍历NF进行UE信息获取恶意行为实验
        for target_nf in emulated_NF_list:
            i = 0
            while i < exp_num:
                # 初始化该恶意NF对象
                evil_nf = EvilNF(target_nf)
                # 创建一个 Manager 对象和一个 list 对象来保存 execut_ue() 的返回值
                manager = multiprocessing.Manager()
                return_values = manager.list()
                def execut_ue_wrapper():
                    # 在 wrapper 函数中调用 execut_ue，并保存返回值
                    return_values.append(execut_ue())
                
                # 创建两个进程
                process1 = multiprocessing.Process(target=execut_ue_wrapper)
                # process2 = multiprocessing.Process(target=evil_nf.ue_info_get, args=(6,3))
                process2 = multiprocessing.Process(target=evil_nf.evil_delete_nf, args=(5,3))
                # 同时启动两个进程，并记录开始时间
                start_time = datetime.now().isoformat()
                process1.start()
                process2.start()

                # 等待两个进程都结束
                process1.join()
                process2.join()
                # 记录结束时间
                end_time = datetime.now().isoformat()


                # 如果 process1 执行的函数返回 True，则记录实验的开始和结束时间
                if return_values[0]:
                    i = i+1
                    with open(time_record_file, 'a') as file:
                        file.write(f"{target_nf} {i} {start_time} {end_time}\n")
                else:
                    # 如果 process1 执行的函数返回 False，则执行 uninstall_5g() 函数
                    uninstall_5g()
                    # 都停止之后重新部署网络
                    deploy_5g()
        gnb_process.kill()
        os.system("kill -9 $(ps -a | grep nr | awk '{print $1}')")
        os.system("kill -9 $(ps -a | grep python | awk '{print $1}')")
        
