# -*- coding: utf-8 -*-
import os
import time
import paramiko
import traceback
import logging
from LogOutput import *


class GetResult:
    def __init__(self):
        self.local_path = ' '
        self.time_stamp = ' '


    ##创建存放本次结果的文件夹，注意这里要以ip区分，local_path结尾不要加/
    def create_loacl_dir(self, local_path):
        self.time_stamp = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
        self.local_path = local_path + self.time_stamp
        os.system('mkdir -p ' + local_path + self.time_stamp)

    ## 拷文件夹，拷每一个测试用例的文件夹，注意到本地之后改名
    def copy_folder_to_here(self, configs, vm_or_compute, remote_path, local_path):
        ##先拷出来
        local_path = self.local_path + '/' + vm_or_compute + '/' +local_path + '/'
        os.system('mkdir -p ' + local_path)
        # 采用密码登录
        if configs['use_public_encryption'] == 'false' or configs['use_public_encryption'] == 'False':
            ssh = paramiko.SSHClient()
            know_host = paramiko.AutoAddPolicy()
            ssh.set_missing_host_key_policy(know_host)
            ssh.connect(configs['host'], configs['ssh_port'], configs['user'], configs['password'])
        # 采用密钥登录
        elif configs['use_public_encryption'] == 'true' or configs['use_public_encryption'] == 'True':
            ssh = paramiko.SSHClient()
            private_key = paramiko.RSAKey.from_private_key_file(configs['rsa_file'], password=configs['password'])
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=configs['host'], username=configs['user'], port=configs['ssh_port'], pkey=private_key)
        else:
            logger.info(configs + 'can not copy file to here.')
            print('please check out your config_machines.yaml-use_public_encryption, and try again.')
            exit(0)
        try:
            sftp = paramiko.SFTPClient.from_transport(ssh.get_transport())
            sftp = ssh.open_sftp()
            remote_files = sftp.listdir(remote_path)
            for file in remote_files:  # 遍历读取远程目录里的所有文件
                local_file = local_path + file
                remote_file = remote_path + file
                sftp.get(remote_file, local_file)
        except IOError:  # 如果目录不存在则抛出异常
            print("remote_path or local_path is not exist")
            msg = traceback.format_exc()
            print(msg)
            return
        ssh.close()


    ## 拷文件，拷集群监控的文件，注意到本地之后改名
    def copy_file_to_here(self, configs, vm_or_compute, remote_file, local_file):
        os.system('mkdir -p ' + self.local_path  + '/ceph_s/' + vm_or_compute + '/')
        local_path = self.local_path + '/ceph_s/' + vm_or_compute + '/' + local_file
        # 采用密码登录
        if configs['use_public_encryption'] == 'false' or configs['use_public_encryption'] == 'False':
            ssh = paramiko.SSHClient()
            know_host = paramiko.AutoAddPolicy()
            ssh.set_missing_host_key_policy(know_host)
            ssh.connect(configs['host'], configs['ssh_port'], configs['user'], configs['password'])
        # 采用密钥登录
        elif configs['use_public_encryption'] == 'true' or configs['use_public_encryption'] == 'True':
            ssh = paramiko.SSHClient()
            private_key = paramiko.RSAKey.from_private_key_file(configs['rsa_file'], password=configs['password'])
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=configs['host'], username=configs['user'], port=configs['ssh_port'], pkey=private_key)
        else:
            logger.error(configs + 'can not copy file to here.')
            print('please check out your config_machines.yaml-use_public_encryption, and try again.')
            exit(0)
        try:
            sftp = paramiko.SFTPClient.from_transport(ssh.get_transport())
            sftp = ssh.open_sftp()
            sftp.get(remote_file, local_path)
        except IOError:  # 如果目录不存在则抛出异常
            msg = traceback.format_exc()
            print(msg)
            print("remote_file is not exist")
            return
        ssh.close()


    ## 重命名远端文件
    def move_remote_files(self, configs, remotefile):
        # 采用密码登录
        if configs['use_public_encryption'] == 'false' or configs['use_public_encryption'] == 'False':
            ssh = paramiko.SSHClient()
            know_host = paramiko.AutoAddPolicy()
            ssh.set_missing_host_key_policy(know_host)
            ssh.connect(configs['host'], configs['ssh_port'], configs['user'], configs['password'])
        # 采用密钥登录
        elif configs['use_public_encryption'] == 'true' or configs['use_public_encryption'] == 'True':
            ssh = paramiko.SSHClient()
            private_key = paramiko.RSAKey.from_private_key_file(configs['rsa_file'], password=configs['password'])
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=configs['host'], username=configs['user'], port=configs['ssh_port'], pkey=private_key)
        else:
            print('please check out your config_machines.yaml-use_public_encryption, and try again.')
            exit(0)
        try:
            stdin, stdout, stderr = ssh.exec_command('sudo mv ' + remotefile + ' ' + remotefile+ self.time_stamp )
        except Exception as e:
            msg = traceback.format_exc()
            print(msg)
            print("ssh connect has exception, please checkout your network and other config, exit.")
            exit(0)
        ssh.close()