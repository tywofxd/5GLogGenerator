### Batch-UERANSIM-Cli

Batch-UERANSIM-Cli基于UERANSIM项目实现批量ue连接5G核心网，并执行其nr-cli所支持的信令，产生丰富多样的5G流量。

#### 一、文件结构介绍

```
.
├── config
│   ├── free5gc
│   └── open5gs
├── current
│   ├── free5gc_current.txt
│   └── open5gs_current.txt
├── free5gc.py
├── free5gc-ue-template.yaml
├── logs
│   ├── free5gc.
│   └── open5gs
├── net5g.py
├── open5gs.py
├── open5gs-ue-template.yaml
├── README.md
├── requirements.txt
├── resources
│   ├── commonConfig.py
│   ├── free5gcConfig.py
│   ├── __init__.py
│   ├── ip.py
│   └── open5gsConfig.py
└── run.py
```

- config 目录用作生成ue的配置文件保存目录，为的是同时启动多个具有不同IMSI的UE进程，模拟多个设备接入核心网，为了简单起见，不为每个UE设置不同的加密信息，切片信息等，除了IMSI外，其他一样
- current 目录中用于保存不同类型的核心网内最后添加的SIM Card的IMSI的最后几位值
- net5g.py Net5GC类，为公共操作函数的封装
- free5gc.py Free5GC类继承自Net5GC
- open5gs.py Open5GS类继承自Net5GC
- resources 一些参数配置，free5gcConfig.py为Free5GC的参数配置，open5gsConfig.py为Open5GS的参数配置，ip.py配置核心网WebUI地址
- run.py 执行操作脚本
- free5gc-ue-template.yaml 用于生成config下面配置信息的模板（free5gc）
- open5gs-ue-template.yaml 用于生成config下面配置信息的模板 (open5gs)
- logs 为各个nr-ue执行的命令的日志信息
- requirements.txt 项目的包依赖

#### 二、知识理论

参考资料

> - UERANSIM - https://github.com/aligungr/UERANSIM
> - Free5GC - https://github.com/free5gc/free5gc
> - Free5GC Docker-Compose - https://github.com/free5gc/free5gc-compose
> - Open5GS - https://open5gs.org/open5gs/docs/
> - Open5GS Docker-Compose - https://github.com/herlesupreeth/docker_open5gs

主要模拟UERANSIM的`nr-cli`命令控制UE操作，由于只存在两个可以在部署好的环境有效的执行的命令，这命令包括`ps-release`、`ps-release-all`、`deregister normal`、`ps-establish`，即模拟PDU会话释放、取消注册和建立PDU会话。



#### 三、操作介绍

依赖包安装 `pip3 install -r requirements.txt`

操作前，打开`resources/ip.py`文件，将`free5gcIP`修改为free5GC核心网安装主机的IP地址或将open5gsIP改为open5gsIP改为Open5GS核心网地址

> Notice: 如果需要使用Open5GS核心网，需要使用参数 --net5gc open5gs

获取一些帮助`python3 run.py -h`

```
usage: run.py [-h] [--sec SEC] [--ue UE] [--simcard SIMCARD] [--net5gc NET5GC]

optional arguments:
  -h, --help         show this help message and exit
  --sec SEC          How long does it run, default 10s
  --ue UE            The number of ues, default 1
  --simcard SIMCARD  The number of SimCards, default 2
  --net5gc NET5GC    The type of 5g core network, 'free5gc' or 'open5gs', default free5gc
```

第一次执行需要先让核心网注册一些IMSI信息，执行命令

```
python3 run.py --simcard 10 --ue 5 --sec 100
```

注意：`--simcard`在核心网注册的UE个数，`--ue`指明启动的UE进程数量，`--time`命名执行的持续时间，以秒为单位。多个UE进程并行执行（多线程方式），期间执行的命令随机上述四个的一个执行。

另外可以将以上命令分两步执行

1. 先注册一些UE在核心网站，`python3 run.py --simcard 10`
2. 多个UE经常并行发送信令到核心网，`python3 run.py --ue 5 --sec 100`

### 四、TroubleShooting
(1) Maybe there are some problem in your core network, please check it.
```python
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
        execute_cmd = "/opt/module/UERANSIM/build/nr-cli -e '%s' %s" % (command, ueId)
        print("LOG:  execute %s" % execute_cmd)
        os.system(execute_cmd)
        timer = 0
        flag = True
        while(True):
            if self._isCommandFinish(command_id, ueId, pduNum_before):
                break
            # 2 minutes, 2*12*5 seconds
            if timer >= 2*12:
                if not flag:
                    raise RuntimeError("Maybe there are some problem in your core network, please check it.")
                self._deregisterByUeId(ueId)
                timer = 0
                flag = False
                
            time.sleep(5)
            timer += 1
```
执行过程中如果出现了`Maybe there are some problem in your core network, please check it.`异常，经过检查，并非核心网异常，尝试修改Net5GC.py下timer的判断范围，增加时长。

(2) 执行一段时间后，UE虚拟化出的网卡消失

出现该问题的原因有一下可能：

① UPF与SMF失联

② AMF出现问题

目前的解决办法是重启核心网