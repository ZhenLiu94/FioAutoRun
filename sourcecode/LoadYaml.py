# -*- coding: utf-8 -*-
import yaml
import os
import re
import time
import traceback

#取消警告提醒
#yaml.warnings({'YAMLLoadWarning': False})

class LoadYaml:
    #'../yamlconfig/config_machines.yaml'   '../yamlconfig/config_fios.yaml'
    def __init__(self, machines_file, fios_file):
        self.watch_cluster_file = '/var/log/cluster_detection_data.out'  # 集群监控的数据输出位置，写死了
        # 获取当前文件路径
        filepath = os.path.dirname(__file__)
        # 获取当前文件的Realpath
        fileNamePath = os.path.split(os.path.realpath(__file__))[0]
        # 获取配置文件的路径，文件不存在抛出异常
        try:
            machines_yaml_path = os.path.join(fileNamePath,machines_file)
            fios_yaml_path = os.path.join(fileNamePath,fios_file)
            f_machines = open(machines_yaml_path, 'r')
            f_fios = open(fios_yaml_path, 'r')
        except IOError:
            msg = traceback.format_exc()
            print(msg)
            print('Error: config file not found, please check your filename and filepath are correct.')
            exit(0)
        # 加载配置文件
        machines_info = f_machines.read()
        fios_info = f_fios.read()
        # 两个yaml的dict
        self.machines_yaml_config = yaml.load(machines_info)
        self.fios_yaml_config = yaml.load(fios_info)
        f_machines.close()
        f_fios.close()


    #设置compute节点信息
    def set_computes_config(self):
        if self.machines_yaml_config['machines_info'].has_key('computes'):
            computes_config = self.machines_yaml_config['machines_info']['computes']
        else:
            computes_config = {}
        return computes_config


    #设置vm节点信息
    def set_vms_config(self):
        if self.machines_yaml_config['machines_info'].has_key('vms'):
            vms_config = self.machines_yaml_config['machines_info']['vms']
        else:
            vms_config = {}
        return vms_config


    #设置池名
    def set_poolname(self):
        poolname = self.machines_yaml_config['machines_info']['poolname']
        return poolname


    #设置rbd大小
    def set_rbdsize(self):
        if self.machines_yaml_config['machines_info'].has_key('rbd_size'):
            rbdsize = int(self.machines_yaml_config['machines_info']['rbd_size'])
        else:
            rbdsize = '0'
        return rbdsize


    def set_stor_mgt(self):
        stor_mgt = self.machines_yaml_config['machines_info']['stor-mgt']
        return stor_mgt


    #设置fio命令信息
    def set_fios_config(self):
        fios_config = {}
        fios_config = self.fios_yaml_config['fio_configs']
        fios_config.pop('fio_result_output')
        fios_config.pop('ioengine')
        fios_config.pop('runtime')
        fios_config.pop('direct')
        return fios_config


    # 设置ioengine
    def set_ioengine(self):
        ioengine = self.fios_yaml_config['fio_configs']['ioengine']
        return ioengine


    #设置测试路径
    def set_mnt(self):
        mnt = '/mnt/autorun' #这里路径写死，耶稣也改不了，我说的！
        return mnt


    #设置direct
    def set_direct(self):
        direct = self.fios_yaml_config['fio_configs']['direct']
        return direct


    #设置运行时间信息
    def set_runtime(self):
        runtime = self.fios_yaml_config['fio_configs']['runtime']
        return runtime


    #设置json输出路径
    def set_json_dir(self):
        json_dir = self.fios_yaml_config['fio_configs']['fio_result_output']
        return json_dir


    #取集群监控数据输出路径
    def set_watch_cluster_file(self):
        return self.watch_cluster_file

