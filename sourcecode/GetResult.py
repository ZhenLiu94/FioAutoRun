# -*- coding: utf-8 -*-
import os
import time
import paramiko

class GetResult:
    def __init__(self):
        self.local_path = ' '


    ##创建存放本次结果的文件夹，注意这里要以ip区分，local_path结尾不要加/
    def create_loacl_dir(self, local_path):
        time_stamp = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
        self.local_path = local_path + time_stamp
        os.system('mkdir -p ' + local_path + time_stamp)

    ## 拷文件夹，拷每一个测试用例的文件夹，注意到本地之后改名
    def copy_folder_to_here(self, configs, vm_or_compute, remote_path, local_path):
        #先拷出来
        local_path = self.local_path + '/' + vm_or_compute + '/' +local_path + '/'
        os.system('mkdir -p ' + local_path)
        ssh = paramiko.SSHClient()
        know_host = paramiko.AutoAddPolicy()
        ssh.set_missing_host_key_policy(know_host)
        scp = paramiko.Transport(configs['host'], configs['ssh_port'])
        scp.connect(username=configs['user'], password=configs['password'])
        sftp = paramiko.SFTPClient.from_transport(scp)
        try:
            remote_files = sftp.listdir(remote_path)
            for file in remote_files:  # 遍历读取远程目录里的所有文件
                local_file = local_path + file
                remote_file = remote_path + file
                sftp.get(remote_file, local_file)
        except IOError:  # 如果目录不存在则抛出异常
            print("remote_path or local_path is not exist")
            return
        scp.close()
        #然后删掉远端
        self.remove_remote_files(configs, remote_path)

    ## 拷文件，拷集群监控的文件，注意到本地之后改名
    def copy_file_to_here(self, configs, vm_or_compute, remote_file, local_file):
        os.system('mkdir -p ' + self.local_path  + '/ceph_s/' + vm_or_compute + '/')
        local_path = self.local_path + '/ceph_s/' + vm_or_compute + '/' + local_file
        ssh = paramiko.SSHClient()
        know_host = paramiko.AutoAddPolicy()
        ssh.set_missing_host_key_policy(know_host)
        scp = paramiko.Transport(configs['host'], configs['ssh_port'])
        scp.connect(username=configs['user'], password=configs['password'])
        sftp = paramiko.SFTPClient.from_transport(scp)
        try:
            sftp.get(remote_file, local_path)
        except IOError:  # 如果目录不存在则抛出异常
            print("remote_file is not exist")
            return
        scp.close()
        #然后删掉远端
        self.remove_remote_files(configs, remote_file)


    ## 删除远端文件
    def remove_remote_files(self, configs, remotefile):
        ssh = paramiko.SSHClient()
        know_host = paramiko.AutoAddPolicy()
        ssh.set_missing_host_key_policy(know_host)
        try:
            ssh.connect(configs['host'], configs['ssh_port'], configs['user'], configs['password'])
            ssh.exec_command('rm -rf ' + remotefile)
        except Exception as e:
            print("ssh connect has exception, please checkout your network and other config, exit.")
            exit(0)