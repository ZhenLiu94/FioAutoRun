# -*- coding: utf-8 -*-
from sourcecode.LoadYaml import *
from sourcecode.DetectionConfig import *
import time


####################################
###拿配置
load_yaml = LoadYaml('../yamlconfig/machines_multy.yaml' , '../yamlconfig/multy_fios.yaml')
computes_config = load_yaml.set_computes_config()
vms_config = load_yaml.set_vms_config()
ioengine = load_yaml.set_ioengine()
mnt = load_yaml.set_mnt()
mnt_dir = mnt + '/test'
direct = load_yaml.set_direct()
runtime = load_yaml.set_runtime()
json_dir = load_yaml.set_json_dir()
poolname = load_yaml.set_poolname()
rbd_size = load_yaml.set_rbdsize()
dd_count = int(rbd_size) * 1024
rbd_real_size = int(rbd_size) + 5
watch_cluster_file = load_yaml.set_watch_cluster_file()
watch_cluster_file_computes = watch_cluster_file + 'compute'
watch_cluster_file_vms = watch_cluster_file + 'vms'
stor_mgt = load_yaml.set_stor_mgt()
fios_config = load_yaml.set_fios_config() #fio信息，这一条要放在最后执行
#把所有compute节点ip取出来
compute_ips = []
if computes_config:
    for i in computes_config.keys():
        compute_ips.append(computes_config[i]['host'])
#把所有vm节点ip取出来
vm_ips = []
if vms_config:
    for i in vms_config.keys():
        vm_ips.append(vms_config[i]['host'])
#把stor-mgt节点ip取出来
stor_mgt_ip = stor_mgt['host']

#############初始化配置文件并获取相应数据
stor_mgt = load_yaml.set_stor_mgt()
#把stor-mgt节点ip取出来
stor_mgt_ip = stor_mgt['host']

if computes_config:
    computes_config = load_yaml.set_computes_config()
    # 把所有compute节点ip取出来
    compute_ips = []
    for i in computes_config.keys():
        compute_ips.append(computes_config[i]['host'])
else:
    pass

if vms_config:
    vms_config = load_yaml.set_vms_config()
    #把所有vm节点ip取出来
    vm_ips = []
    for i in vms_config.keys():
        vm_ips.append(vms_config[i]['host'])
else:
    pass



#############初始化检测对象
check_config = DetectionConfig()

print("let's checkout your config.")
#############检测ip是否合法
time.sleep(1)
print("1. Whether your IPs are legally: ")
check_config.is_ip_illegal(stor_mgt_ip, "stor-mgt ip")
if computes_config:
    check_config.is_ips_illegal(compute_ips, "compute ips")
    check_config.is_ips_repetition(compute_ips, "compute ips")
else:
    pass
if vms_config:
    check_config.is_ips_repetition(vm_ips, "vm ips")
    check_config.is_ips_illegal(vm_ips, "vm ips")
else:
    pass
print("    All IPs are leagally, continue...")


#############检测fio的json路径是否加了/
print("2. Whether your fio output dir add / in final location: ")
if json_dir[-1] == '/':
    print("    fio output dir is right, continue...")
else:
    print("    Error: fio_result_output need to hava / in final location, please add it and try again.")
    exit(0)


#############检测ip是否可连接
time.sleep(1)
print("3. Whether your IPs can connected: ")
connect_sshs_computers = []   #两个连接池---计算
connect_sshs_vms = []         #两个连接池---虚拟

if computes_config:
    for i in computes_config.keys():
        connect_sshs_computers.append(check_config.connect_ssh(computes_config[i]))
else:
    pass
if vms_config:
    for i in vms_config.keys():
        connect_sshs_vms.append(check_config.connect_ssh(vms_config[i]))
else:
    pass
print("    All IPs can connected, continue...")


#############检测计算节点是否安装fio
time.sleep(1)
if computes_config:
    print("4. Whether your computes are installed fio command: ")
    check_config.is_installed_fio(connect_sshs_computers, "compute")


#############检测虚机节点是否安装fio
time.sleep(1)
if vms_config:
    print("5. Whether your vms are installed fio command: ")
    check_config.is_installed_fio(connect_sshs_vms, "vm")


#############断开连接
if computes_config:
    for j in connect_sshs_computers:
        check_config.close_ssh(j)
else:
    pass
if vms_config:
    for j in connect_sshs_vms:
        check_config.close_ssh(j)
else:
    pass


#############检测虚机中的盘是否被挂载
time.sleep(1)
if vms_config:
    print("6. Whether your vms' disk are umounted: ")
    for i in vms_config.keys():
        check_config.is_device_mounted(vms_config[i])
    if check_config.is_umounted == True:
        print("    All disk may not mounted, continue...")
    else:
        print("    Error: Maybe you have to checkout your disk configuration...")
        exit(0)
else:
    pass


print("checkout finished, please use 'python multy.py' to start your fio test.")











