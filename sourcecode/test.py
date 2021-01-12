# -*- coding: utf-8 -*-
# import paramiko
# import logging
# import os
# import re

# 测试日志
# logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)
# test = logging.StreamHandler()
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# test.setFormatter(formatter)
# logger.addHandler(test)
# logger.info("dddd")

# 测试连接
# ssh = paramiko.SSHClient()
# know_host = paramiko.AutoAddPolicy()
# ssh.set_missing_host_key_policy(know_host)
# ssh.connect( )
#
# stdin, stdout, stderror = ssh.exec_command('fio')
# res, err = stdout.read(), stderror.read()
#
# if res:
#     print('ok')
# else:
#     print('false')
# result = res if res else err
# print result.decode()

# 测试硬盘挂载
# ssh = paramiko.SSHClient()
# know_host = paramiko.AutoAddPolicy()
# ssh.set_missing_host_key_policy(know_host)
# ssh.connect( )
#
# stdin, stdout, stderror = ssh.exec_command('sudo lsblk -b /dev/vdc')
# res, err = stdout.read(), stderror.read()
# output = res if res else err
# result = str(output.decode())
# data = result.splitlines()[1]
# data = data.replace(' ', '-')
# print data
# if result.find('/') > 0 or result.find('lvm') > 0:
#     print("false")
# else:
#     print("True")

# 测试去掉字符串最后一个字符
# a = "abcdefg/"
# a = a[:-1]
# print a


# 列举文件夹下文件
# def get_files_list(path):
#     files_list = []
#     files = os.listdir(path)
#     for tmp_file in files:
#         path_file = os.path.join(path, tmp_file)
#         if os.path.isdir(path_file) and not os.path.islink(path_file):
#             files_list.append(path_file)
#             files_list += self.getList(path_file)
#         else:
#             files_list.append(path_file)
#     print files_list
#     return files_list

# 测试把文件拷贝到远端以及拷回来
# ssh = paramiko.SSHClient()
# know_host = paramiko.AutoAddPolicy()
# ssh.set_missing_host_key_policy(know_host)
# ssh.connect( )
# sftp = paramiko.SFTPClient.from_transport(ssh.get_transport())
# sftp = ssh.open_sftp()
# remote_files = sftp.listdir('/etc/ceph')
# for file in remote_files:  # 遍历读取远程目录里的所有文件
#     local_file = './ceph/' + file
#     remote_file = '/etc/ceph/' + file
#     sftp.get(remote_file, local_file)

# all_files = get_files_list('./ceph')
# for file in all_files:
#     sftp.put(file, '/root/liuzhen/' + file.split('/')[-1])
