# -*- coding: utf-8 -*-
from sourcecode.LoadYaml import *
from sourcecode.DetectionConfig import *

#初始化配置文件并获取相应数据
load_yaml = LoadYaml()
computes_config = load_yaml.set_computes_config()
vms_config = load_yaml.set_vms_config()
stor_mgt = load_yaml.set_stor_mgt()

#把所有compute节点ip取出来
compute_ips = []
for i in computes_config.keys():
    compute_ips.append(computes_config[i]['host'])

#把所有vm节点ip取出来
vm_ips = []
for i in vms_config.keys():
    vm_ips.append(vms_config[i]['host'])

#把stor-mgt节点ip取出来
stor_mgt_ip = stor_mgt['host']

#检测ip是否合法
is_ip_illegal(stor_mgt_ip)
is_ips_illegal(compute_ips)
is_ips_illegal(vm_ips)
is_ips_repetition(compute_ips)
is_ips_repetition(vm_ips)
