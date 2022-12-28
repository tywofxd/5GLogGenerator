### Batch-UERANSIM-Cli

#### 一、文件结构介绍

```
├── config
│   ├── free5g-ue-imsi-208930000000004.yaml
│   └── free5g-ue-imsi-208930000000005.yaml
├── current.txt
├── free5gc.py
├── free5gc-ue-template.yaml
├── nohup.out
├── README.md
├── resources.py
├── requirements.txt
└── run.py
```

- config 目录用作生成free5gc-ue的配置文件保存目录，为的是同时启动多个具有不同IMSI的UE进程，模拟多个设备接入核心网，为了简单起见，不为每个UE设置不同的加密信息，切片信息等，除了IMSI外，其他洞一样
- current.txt 用于保存当前核心网内最后添加的SIM Card的IMSI的最后几位值
- free5gc.py 为用于操作的函数
- resources.py 一些使用到的变量
- run.py 执行操作脚本
- free5gc-ue-template.yaml 用于生成config下面配置信息的模板
- nohub.out为所以nr-ue执行的命令的日志信息
- requirements.txt 项目的包依赖

#### 二、知识理论

参考资料

> - UERANSIM - https://github.com/aligungr/UERANSIM
> - Free5GC - https://github.com/free5gc/free5gc
> - Free5GC Docker-Compose - https://github.com/free5gc/free5gc-compose

主要模拟UERANSIM的`nr-cli`命令控制UE操作，由于只存在两个可以在部署好的环境有效的执行的命令，这命令包括`ps-release`、`ps-release-all`、`deregister normal`、`ps-establish`，即模拟PDU会话释放、取消注册和建立PDU会话。



#### 三、操作介绍

依赖包安装 `pip3 install -r requirements.txt`

操作前，打开`resources.py`文件，将`free5gcIP`修改为free5GC核心网安装主机的IP地址

获取一些帮助`python3 run.py -h`

```
usage: free5gc.py [-h] [--sec SEC] [--ue UE] [--simcard SIMCARD]

optional arguments:
  -h, --help         show this help message and exit
  --sec SEC          How long does it run, default 10s
  --ue UE            The number of ues, default 1
  --simcard SIMCARD  The number of SimCards, default 2
```

第一次执行需要先让核心网注册一些IMSI信息，执行命令

```
python3 run.py --simcard 10 --ue 5 --sec 100
```

注意：`--simcard`在核心网注册的UE个数，`--ue`指明启动的UE进程数量，`--time`命名执行的持续时间，以秒为单位。多个UE进程并行执行（多线程方式），期间执行的命令随机上述四个的一个执行。

另外可以将以上命令分两步执行

1. 先注册一些UE在核心网站，`python3 run.py --simcard 10`
2. 多个UE经常并行发送信令到核心网，`python3 run.py --ue 5 --sec 100`
