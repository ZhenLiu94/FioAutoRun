# -*- coding: utf-8 -*-

import sys
from sourcecode.LoadYaml import *
from sourcecode.SpellFio import *
from sourcecode.DetectionConfig import *
from sourcecode.RunSSH import *
from sourcecode.PreConfig import *
from sourcecode.GetResult import *
from sourcecode.DoExcel import *
from sourcecode.LogOutput import *


####################################
###再思考一下还有配错的吗？
for i in range(1, 5):
    print("program will start after " + str(5-i) + " seconds later...")
    time.sleep(1)

####################################
###拿配置
load_yaml = LoadYaml('../yamlconfig/machines_single.yaml' , '../yamlconfig/single_fios.yaml')
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
rbd_real_size = int(rbd_size) + int(rbd_size/10)
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


####################################
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


####################################
###初始化预处理对象
pre_config = PreConfig()


####################################
###执行计算节点fio
if computes_config:
    #先把stor-mgt节点配置文件拷过来
    pre_config.get_config_from_stormgt(stor_mgt)
    #再把这个配置文件拷到远端compute节点
    for i in computes_config.keys():
        pre_config.put_config_to_computes(computes_config[i])
    #初始化跑fio的ssh类
    run_ssh_computers = RunSSH(fio_iops_bw_commands_computers, fio_lat_commands_computers, computes_config, vms_config, stor_mgt, watch_cluster_file_computes, runtime, poolname)
    connect_sshs_computers = []
    for i in computes_config.keys():
        connect_sshs_computers.append(run_ssh_computers.connect_ssh(computes_config[i]))
    # 创建rbd，大小是单位是G
    pre_config.create_and_map_rbd(connect_sshs_computers, poolname, rbd_real_size, mnt)
    # 创建json文件夹
    pre_config.create_dir(connect_sshs_computers, json_dir)
    # dd写文件的大小，单位是M，例如100就是100M，因为块是1M，记住，如果这里改了，要在fio配置文件那里也改
    pre_config.dd_file(connect_sshs_computers, mnt_dir, dd_count)
    try:
        #执行命令
        run_ssh_computers.run_compute_lat_command(computes_config, fio_lat_commands_computers)
        run_ssh_computers.run_fio_command(computes_config, fio_iops_bw_commands_computers)
    except Exception as e:
        print(e)
    try:
        pre_config.del_rbd(connect_sshs_computers, poolname, mnt)
    except Exception as e:
        print e
        print("del rbd failed.")

    for j in connect_sshs_computers:
        run_ssh_computers.close_ssh(j)
    #把本机下载下来的配置文件再删掉
    pre_config.del_local_download_config()
    for i in computes_config.keys():
        pre_config.back_compute_config(computes_config[i])
else:
    pass

####################################
###把文件拷出来
get_result = GetResult()
get_result.create_loacl_dir('./autofiooutput')#结尾不要加/
if computes_config:
    get_result.copy_file_to_here(stor_mgt, 'compute', watch_cluster_file_computes, 'computes.data')
    for i in computes_config.keys():
        get_result.copy_folder_to_here(computes_config[i], 'compute', json_dir, str(computes_config[i]['host']))
    # 移动文件
    get_result.move_remote_files(stor_mgt, watch_cluster_file_computes)
    # 移动文件夹
    temp_json_dir = json_dir[:-1]
    for i in computes_config.keys():
        get_result.move_remote_files(computes_config[i], temp_json_dir)
else:
    pass

####################################
###生成计算节点excel
#非空才执行
if computes_config:
    save_path = r"./"
    xlsx_name = "autotest_compute_single"
    workbook = DoExcel(save_path + xlsx_name + '.xlsx', xlsx_name)
    folder_name = workbook.get_location('compute')
    fio_path = './' + get_result.local_path + '/' + folder_name + '/'
    ceph_s_path = './' + get_result.local_path + '/ceph_s/' + folder_name + '/'
    #取数据
    lat_data, iops_bw_data = workbook.parse_json(fio_path, ceph_s_path)
    workbook.to_excel(lat_data, iops_bw_data, len(compute_ips))
    workbook.workbook.close()
else:
    pass
