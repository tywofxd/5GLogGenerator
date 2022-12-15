### Batch-UERANSIM-Cli

#### 一、文件结构介绍

```
├── config
│   ├── free5g-ue-imsi-208930000000004.yaml
│   ├── free5g-ue-imsi-208930000000005.yaml
│   ├── free5g-ue-imsi-208930000000006.yaml
│   └── free5g-ue-imsi-208930000000007.yaml
├── current.txt
├── free5gc.py
├── free5gc-ue-template.yaml
├── nohup.out
└── README.md
```

- config 目录用作生成free5gc-ue的配置文件保存目录，为的是同时启动多个具有不同IMSI的UE进程，模拟多个设备接入核心网，为了简单起见，不为每个UE设置不同的加密信息，切片信息等，除了IMSI外，其他洞一样
- current.txt 用于保存当前核心网内最后添加的SIM Card的IMSI的最后几位值
- free5gc.py 为操作脚本，具体在后面介绍
- free5gc-ue-template.yaml 用于生成config下面配置信息的模板
- nohub.out为所以nr-ue执行的命令的日志信息

#### 二、知识理论

参考资料

> - UERANSIM - https://github.com/aligungr/UERANSIM
> - Free5GC - https://github.com/free5gc/free5gc
> - Free5GC Docker-Compose - https://github.com/free5gc/free5gc-compose

主要模拟UERANSIM的`nr-cli`命令控制UE操作，由于只存在两个可以在部署好的环境有效的执行的命令，这命令包括`ps-release-all`、`deregister normal`，即模拟PDU会话释放和取消注册。经验证，执行释放PDU会话后2-3秒内自动重新建立，执行取消注册后10秒内重新自动注册。如果需要产生足够的注册数据的，启动更多UE即可，参数为`--startue`



#### 三、操作介绍

操作前，打开`free5gc.py`文件，将`free5gcIP`修改为free5GC核心网安装主机的IP地址

获取一些帮助`python3 free5gc.py -h`

```
usage: free5gc.py [-h] [--cmd CMD] [--ue UE] [--enable] [--startue]
                  [--simcard SIMCARD]

optional arguments:
  -h, --help         查看脚本的帮助信息
  --cmd CMD          模拟产生多少个命令，默认值为 1
  --ue UE            模拟启动UE的数量，默认值为 1
  --enable           是否在核心网生成合法用户设备UE的信息，使用该参数则启动，默认值为 False
  --startue          是否启动UE进程接入核心网，默认值为 True
  --simcard SIMCARD  在启动核心网生成数据后，可指定生成合法用户信息的数量，默认值为 2
```

第一次执行需要先让核心网注册一些IMSI信息，执行命令

```
python3 free5gc.py --enable --simcard 10 --ue 5 --cmd 100
```

注意：`--enable，--simcard`配合使用，如果不启用`--enable`，`--simcard`参数将无效；`--startue`可以控制不执行启动UE，使用上一次执行使用的UE进程

第二次执行时，可以不加`--startue`，另外可以增加`--enable`，可以说此时该参数完全不必要的，如果需要在核心网生成更多的SIM Card信息时，可以执行（根据需要更改）。
