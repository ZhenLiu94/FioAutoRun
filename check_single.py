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
computes_config = load_yaml.set_computes_config()
stor_mgt = load_yaml.set_stor_mgt()
#把所有compute节点ip取出来
compute_ips = []
for i in computes_config.keys():
    compute_ips.append(computes_config[i]['host'])
#把stor-mgt节点ip取出来
stor_mgt_ip = stor_mgt['host']


#############初始化检测对象
check_config = DetectionConfig()

print("let's checkout your config.")
#############检测ip是否合法
time.sleep(1)
print("1. Whether your IPs are legally: ")
check_config.is_ip_illegal(stor_mgt_ip, "stor-mgt ip")
check_config.is_ips_illegal(compute_ips, "compute ips")
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
for i in computes_config.keys():
    connect_sshs_computers.append(check_config.connect_ssh(computes_config[i]))
print("    All IPs can connected, continue...")


#############检测计算节点是否安装fio
time.sleep(1)
print("4. Whether your computes are installed fio command: ")
check_config.is_installed_fio(connect_sshs_computers, "compute")


#############断开连接
for j in connect_sshs_computers:
    check_config.close_ssh(j)


print("checkout finished, please use 'python single.py' to start your fio test.")











