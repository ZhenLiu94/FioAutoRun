# -*- coding: utf-8 -*-
import time
import paramiko
import os
import re

class PreConfig:
    def __init__(self):
        self.rbd_dict = [] #存rbd的map信息


    # 这里是跑创建文件夹的
    def create_dir(self, ssh_connects, dir_list):
        for ssh_connect in ssh_connects:
            stdin, stdout, stderr = ssh_connect.exec_command('sudo rm -rf ' + dir_list)    # 先删除旧的
            # 加上这两行说明需要等待执行完，防止创建失败
            res, err = stdout.read(), stderr.read()
            result = res if res else err
            stdin, stdout, stderr = ssh_connect.exec_command('sudo mkdir -p ' + dir_list)  # 再创建新的
            # 加上这两行说明需要等待执行完，防止创建失败
            res, err = stdout.read(), stderr.read()
            result = res if res else err


    # 这里是跑删除文件夹的，要小心，别把系统文件夹删了，慎用
    def remove_dir(self, ssh_connects, dir_list):
        for ssh_connect in ssh_connects:
            stdin, stdout, stderr = ssh_connect.exec_command('sudo rm -rf ' + dir_list)    # 删除
            # 加上这两行说明需要等待执行完，防止创建失败
            res, err = stdout.read(), stderr.read()
            result = res if res else err


    # 检测是否执行完dd的
    def is_dd_finfished(self, ssh_connects, mnt):
        while True:
            is_dd_finished = []
            is_all_finish = False
            time.sleep(5)
            for check_dd in ssh_connects:
                check_stdin, check_stdout, check_stderr = check_dd.exec_command('sudo ps -ef|grep dd|grep /dev/zero')
                res, err = check_stdout.read(), check_stderr.read()
                result = res if res else err
                if 'count=' not in str(result.decode()):
                    is_dd_finished.append(True)
                else:
                    is_dd_finished.append(False)
            if False in is_dd_finished:
                print('is all dd command finished: ' + str(is_dd_finished))
                pass
            else:
                is_all_finish = True  # 保证所有命令都执行完了
                print('is all dd command finished: ' + str(is_dd_finished))
                for rm_dd in ssh_connects:
                    stdin, stdout, stderr = rm_dd.exec_command('sudo rm -rf ' + mnt)
                break

    # 这里是dd写文件的，dd写一次就行
    def dd_file(self, ssh_connects, mnt, size):
        time.sleep(5)
        # 开始写入
        for ssh_connect in ssh_connects:
            check_stdin, check_stdout, check_stderr = ssh_connect.exec_command('sudo dd if=/dev/zero of=' + mnt + ' count='  + str(size) + ' bs=1M')
        # 检测是否写完
        self.is_dd_finfished(ssh_connects, mnt)


    #如果要改rbdname那个/autofio，记得把底下del_rbd的rbdname一并改掉
    def create_and_map_rbd(self, ssh_connects, poolname, size, mnt_dir):
        for ssh_connect in ssh_connects:
            rbdname = '/autofio' + ssh_connect._host_keys._entries[0].hostnames[0]
            # 先挂载rbd
            stdin, stdout, stderr = ssh_connect.exec_command('sudo rbd create ' + poolname + rbdname +
                                                             ' --size ' + str(size) +
                                                             'G;sudo rbd feature disable ' +
                                                             poolname + rbdname +' object-map fast-diff deep-flatten;')
            # 加上这两行说明需要等待执行完，防止创建失败
            res, err = stdout.read(), stderr.read()
            result = res if res else err
            # 然后map rbd
            rbd_stdin, rbd_stdout, rbd_stderr = ssh_connect.exec_command('sudo rbd map ' + poolname + rbdname)
            res, err = rbd_stdout.read(), rbd_stderr.read()
            result = res if res else err
            rbd_info = str(result.decode()).strip()
            # 然后mount加格式化
            stdin, stdout, stderr = ssh_connect.exec_command('sudo mkfs.xfs -f ' + rbd_info +
                                                             ';sudo mkdir -p ' + mnt_dir +
                                                             ';sudo mount ' + rbd_info + ' ' +
                                                             mnt_dir + ';')
            # 加上这两行说明需要等待执行完，防止创建失败
            res, err = stdout.read(), stderr.read()
            result = res if res else err

    # 如果要改rbdname那个/autofio，记得把底下del_rbd的rbdname一并改掉
    def del_rbd(self, ssh_connects, poolname, mnt_dir):
        for ssh_connect in ssh_connects:
            rbdname = '/autofio' + ssh_connect._host_keys._entries[0].hostnames[0]
            stdin, stdout, stderr = ssh_connect.exec_command('sudo umount ' + mnt_dir + ';' +
                                                             'sudo rm -rf ' + mnt_dir + ';' +
                                                             'sudo rbd unmap ' + poolname +
                                                             rbdname + ';sudo rbd rm ' + poolname + rbdname)
            # 加上这两行说明需要等待执行完，防止创建失败
            res, err = stdout.read(), stderr.read()
            result = res if res else err


    # 从stor-mgt节点向本机拷ceph配置文件
    def get_config_from_stormgt(self, stor_configs):
        os.system('sudo mkdir -p ./ceph')
        os.system('sudo chmod -R 777 ./ceph')
        # 采用密码登录
        if stor_configs['use_public_encryption'] == 'false' or stor_configs['use_public_encryption'] == 'False':
            ssh = paramiko.SSHClient()
            know_host = paramiko.AutoAddPolicy()
            ssh.set_missing_host_key_policy(know_host)
            ssh.connect(stor_configs['host'], stor_configs['ssh_port'], stor_configs['user'], stor_configs['password'])
        # 采用密钥登录
        elif stor_configs['use_public_encryption'] == 'true' or stor_configs['use_public_encryption'] == 'True':
            ssh = paramiko.SSHClient()
            private_key = paramiko.RSAKey.from_private_key_file(stor_configs['rsa_file'], password=stor_configs['password'])
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=stor_configs['host'], username=stor_configs['user'], port=stor_configs['ssh_port'], pkey=private_key)
        else:
            print('please check out your config_machines.yaml-use_public_encryption, and try again.')
            exit(0)
        try:
            sftp = paramiko.SFTPClient.from_transport(ssh.get_transport())
            sftp = ssh.open_sftp()
            remote_files = sftp.listdir('/etc/ceph')
            for file in remote_files:  # 遍历读取远程目录里的所有文件
                local_file = './ceph/' + file
                remote_file = '/etc/ceph/' + file
                sftp.get(remote_file, local_file)
        except IOError:  # 如果目录不存在则抛出异常
            print("remote_path or local_path is not exist")
            msg = traceback.format_exc()
            print(msg)
            return
        ssh.close()
        os.system('sudo chmod -R 777 ./ceph ')


    # 列举文件夹下文件
    def get_files_list(self, path):
        files_list = []
        files = os.listdir(path)
        for tmp_file in files:
            path_file = os.path.join(path, tmp_file)
            if os.path.isdir(path_file) and not os.path.islink(path_file):
                files_list.append(path_file)
                files_list += self.getList(path_file)
            else:
                files_list.append(path_file)
        return files_list


    # 把本机从stor-mgt中取到的配置文件拷到远端compute节点
    def put_config_to_computes(self, compute_configs):
        # 采用密码登录
        if compute_configs['use_public_encryption'] == 'false' or compute_configs['use_public_encryption'] == 'False':
            ssh = paramiko.SSHClient()
            know_host = paramiko.AutoAddPolicy()
            ssh.set_missing_host_key_policy(know_host)
            ssh.connect(compute_configs['host'], compute_configs['ssh_port'], compute_configs['user'], compute_configs['password'])
        # 采用密钥登录
        elif compute_configs['use_public_encryption'] == 'true' or compute_configs['use_public_encryption'] == 'True':
            ssh = paramiko.SSHClient()
            private_key = paramiko.RSAKey.from_private_key_file(compute_configs['rsa_file'], password=compute_configs['password'])
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=compute_configs['host'], username=compute_configs['user'], port=compute_configs['ssh_port'], pkey=private_key)
        else:
            print('please check out your config_machines.yaml-use_public_encryption, and try again.')
            exit(0)
        #先把远端ceph配置备份一下
        stdin, stdout, stderr = ssh.exec_command("sudo mkdir -p /etc/ceph && sudo mv /etc/ceph /etc/cephbak && sudo mkdir -p /etc/ceph")
        #再把本机的ceph配置拷过去
        sftp = paramiko.SFTPClient.from_transport(ssh.get_transport())
        sftp = ssh.open_sftp()
        all_files = self.get_files_list('./ceph')
        for file in all_files:
            try:
                sftp.put(file, '/etc/ceph/' + file.split('/')[-1])
            except IOError:
                print('machine ip: ' + compute_configs['host'])
                print('local filename: ' + file)
                print('remote filename: ' + '/etc/ceph/' + file.split('/')[-1])



    # 把远端计算节点的配置文件改回来
    def back_compute_config(self, compute_configs):
        # 采用密码登录
        if compute_configs['use_public_encryption'] == 'false' or compute_configs['use_public_encryption'] == 'False':
            ssh = paramiko.SSHClient()
            know_host = paramiko.AutoAddPolicy()
            ssh.set_missing_host_key_policy(know_host)
            ssh.connect(compute_configs['host'], compute_configs['ssh_port'], compute_configs['user'], compute_configs['password'])
        # 采用密钥登录
        elif compute_configs['use_public_encryption'] == 'true' or compute_configs['use_public_encryption'] == 'True':
            ssh = paramiko.SSHClient()
            private_key = paramiko.RSAKey.from_private_key_file(compute_configs['rsa_file'], password=compute_configs['password'])
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=compute_configs['host'], username=compute_configs['user'], port=compute_configs['ssh_port'], pkey=private_key)
        else:
            print('please check out your config_machines.yaml-use_public_encryption, and try again.')
            exit(0)
        ssh.exec_command("sudo rm -rf /etc/ceph && sudo mv /etc/cephbak /etc/ceph")
        ssh.close()


    # 删掉本机的配置文件
    def del_local_download_config(self):
        os.system('sudo rm -rf ./ceph/*')
