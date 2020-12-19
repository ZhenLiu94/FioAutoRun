# -*- coding: utf-8 -*-

from sourcecode.LoadYaml import *
from sourcecode.SpellFio import *
from sourcecode.DetectionConfig import *
from sourcecode.RunSSH import *
from sourcecode.PreConfig import *
from sourcecode.GetResult import *
from sourcecode.DoExcel import *

##给你5秒钟思考时间，反悔还来得及，不然rbd可得自己删了哈！耗子尾汁
#print('5s later, autofio start......')
#time.sleep(5)

#初始化配置文件并获取相应数据
load_yaml = LoadYaml()
computes_config = load_yaml.set_computes_config()
vms_config = load_yaml.set_vms_config()
ioengine = load_yaml.set_ioengine()
mnt = load_yaml.set_mnt()
mnt_dir = mnt + '/test'
direct = load_yaml.set_direct()
runtime = load_yaml.set_runtime()
json_dir = load_yaml.set_json_dir()
poolname = load_yaml.set_poolname()
watch_cluster_file = load_yaml.set_watch_cluster_file()
watch_cluster_file_computes = watch_cluster_file + 'compute'
watch_cluster_file_vms = watch_cluster_file + 'vms'
stor_mgt = load_yaml.set_stor_mgt()
fios_config = load_yaml.set_fios_config() #fio信息，这一条要放在最后执行

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

######################################################################################
###拼接命令
#拼接fio命令
load_fios = SpellFio()
fio_commands_vms = load_fios.spell_fio(json_dir, ioengine, runtime, mnt_dir, direct, fios_config)
fio_commands_computers = load_fios.spell_fio(json_dir, ioengine, runtime, mnt_dir, direct, fios_config)
#取iops和bw的命令
fio_iops_bw_commands_vms = load_fios.get_iops_bw_commands(fio_commands_vms)
fio_iops_bw_commands_computers = load_fios.get_iops_bw_commands(fio_commands_computers)
#取lat的命令
fio_lat_commands_vms = load_fios.get_lat_commands(fio_commands_vms)
fio_lat_commands_computers = load_fios.get_lat_commands(fio_commands_computers)
######################################################################################
###拼接命令结束
# pre_config = PreConfig()
#
#
# ######################################################################################
# ###计算节点
# #初始化跑fio的ssh类
# run_ssh_computers = RunSSH(fio_iops_bw_commands_computers, fio_lat_commands_computers, computes_config, vms_config, stor_mgt, watch_cluster_file_computes, runtime, poolname)
# connect_sshs_computers = []
# for i in computes_config.keys():
#     connect_sshs_computers.append(run_ssh_computers.connect_ssh(computes_config[i]))
# # 创建rbd，大小是单位是G
# pre_config.create_and_map_rbd(connect_sshs_computers, poolname, 100, mnt)
# # 创建json文件夹
# pre_config.create_dir(connect_sshs_computers, json_dir)
# # dd写文件的大小，单位是M，例如100就是100M，因为块是1M，记住，如果这里改了，要在fio配置文件那里也改
# pre_config.dd_file(connect_sshs_computers, mnt_dir, 102400)
#
# #执行命令
# run_ssh_computers.run_compute_lat_command(computes_config, fio_lat_commands_computers)
# run_ssh_computers.run_fio_command(computes_config, fio_iops_bw_commands_computers)
#
#
# pre_config.del_rbd(connect_sshs_computers, poolname, mnt)
#
# for j in connect_sshs_computers:
#     run_ssh_computers.close_ssh(j)
# ######################################################################################
# ###计算节点结束
#
# ######################################################################################
# ###虚拟机节点
# #初始化跑fio的ssh类
# run_ssh_vms = RunSSH(fio_iops_bw_commands_computers, fio_lat_commands_computers, computes_config, vms_config, stor_mgt, watch_cluster_file_vms, runtime, poolname)
# connect_sshs_vms = []
# for i in vms_config.keys():
#     #connect_sshs_vms.append(run_ssh_vms.connect_ssh(vms_config[i]))
#     connect_sshs_vms.append(run_ssh_vms.connect_ssh_mount(vms_config[i], mnt)) #真实测试用这个，需要带着mount
# # 创建json文件夹
# pre_config.create_dir(connect_sshs_vms, json_dir)
#
# # dd写文件的大小，单位是M，例如100就是100M，因为块是1M，记住，如果这里改了，要在fio配置文件那里也改
# pre_config.dd_file(connect_sshs_vms, mnt_dir, 102400)
# # 执行命令
# run_ssh_vms.run_vm_lat_command(vms_config, fio_lat_commands_vms)
# run_ssh_vms.run_fio_command(vms_config, fio_iops_bw_commands_vms)
#
# for j in connect_sshs_vms:
#     #run_ssh_vms.close_ssh(j)
#     run_ssh_vms.close_ssh_umount(j, mnt) #真实测试用这个，需要带删除文件和umount
# ######################################################################################
# ###虚拟机节点结束
#
# ######################################################################################
# ###把文件拷出来
# get_result = GetResult()
# get_result.create_loacl_dir('./autofiooutput')#结尾不要加/
# get_result.copy_file_to_here(stor_mgt, 'compute', watch_cluster_file_computes, 'computes.data')
# get_result.copy_file_to_here(stor_mgt, 'vm', watch_cluster_file_vms, 'vms.data')
# for i in computes_config.keys():
#     get_result.copy_folder_to_here(computes_config[i], 'compute', json_dir, str(computes_config[i]['host']))
# for j in vms_config.keys():
#     get_result.copy_folder_to_here(vms_config[j], 'vm', json_dir, str(vms_config[j]['host']))
# ######################################################################################
# ###把文件拷出来结束
#
# ######################################################################################
# ###生成excel
#
# ##生成excel的文件名，不用加后缀
xlsx_name = "autotest"
##生成excelsheet的名字
sheet_name = ""
## fio数据路径
fio_path = "C:/Users/liiuzhen/Desktop/fioformat/autofiooutput2020-12-18-13-02-35/compute/"
## ceph-s数据路径
ceph_s_path = r"C:/Users/liiuzhen/Desktop/fioformat/autofiooutput2020-12-18-13-02-35/ceph_s/compute/"
## 生成excel所在路径
save_path = r"./"

workbook = DoExcel(save_path + xlsx_name + '.xlsx', sheet_name)
lat_data, iops_bw_data = workbook.parse_json(fio_path, ceph_s_path)
workbook.to_excel(lat_data, iops_bw_data, 3)
workbook.workbook.close()
######################################################################################
###生成excel结束

















