# -*- coding: utf-8 -*-
import re
import paramiko


class DetectionConfig:
    def __init__(self):
        self.is_umounted = True


    # 检测ip们是否合法
    def is_ips_illegal(self, ipAddrs, checkname):
        result = True
        compile_ip = re.compile(
            '^(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|[1-9])\.(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)\.(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)\.(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)$')
        for ip in ipAddrs:
            if compile_ip.match(ip):
                continue
            else:
                print('    ERROR: ' + checkname + ': ' + ip + ' False, please checkout you ip input.')
                result = False
                exit(0)
        return result


    # 检测ip是否合法
    def is_ip_illegal(self, ipAddr, checkname):
        result = True
        compile_ip = re.compile(
            '^(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|[1-9])\.(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)\.(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)\.(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)$')
        if compile_ip.match(ipAddr):
            pass
        else:
            print('    ERROR: ' + checkname + ': ' + ipAddr + ' False, please checkout you ip input.')
            result = False
            exit(0)
        return result


    # 检测是否有重复ip，需要传入所有fio的ip地址
    def is_ips_repetition(self, ipAddrs, checkname):
        none_repetition = list(set(ipAddrs))
        if len(ipAddrs) == len(none_repetition):
            return True
        else:
            print("    ERROR: "  + checkname + " testing have repetition ip, please checkout and run again.")
            return False
            exit(0)

    ## 连接ssh
    def connect_ssh(self, configs):
        try:
            # 采用密码登录
            if configs['use_public_encryption'] == 'false' or configs['use_public_encryption'] == 'False':
                ssh = paramiko.SSHClient()
                know_host = paramiko.AutoAddPolicy()
                ssh.set_missing_host_key_policy(know_host)
                ssh.connect(configs['host'], configs['ssh_port'], configs['user'], configs['password'])
            # 采用密钥登录
            elif configs['use_public_encryption'] == 'true' or configs['use_public_encryption'] == 'True':
                ssh = paramiko.SSHClient()
                private_key = paramiko.RSAKey.from_private_key_file(configs['rsa_file'],
                                                                    password=configs['password'])
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(hostname=configs['host'], username=configs['user'], port=configs['ssh_port'],
                            pkey=private_key)
            else:
                print('    Error: please check out your config_machines.yaml-use_public_encryption, and try again.')
                exit(0)
        except Exception as e:
            print("    Error: " + configs['host'] + " ssh connect has exception, please checkout your network and other config, exit.")
            exit(0)
        return ssh


    ## 断开ssh
    def close_ssh(self, ssh_connect):
        try:
            ssh_connect.close()
        except Exception as e:
            print("    Error: " + configs['host'] + " ssh disconnect has exception, exit.")
            exit(0)

    # 检测是否安装fio
    def is_installed_fio(self, connect_sshs, vm_or_compute):
        check_fio = True
        for i in connect_sshs:
            stdin, stdout, stderror = i.exec_command('fio')
            res, err = stdout.read(), stderror.read()
            if res:
                continue
            else:
                print("    Error: " + i._host_keys._entries[0].hostnames[0] + ' do not have fio, please install first.')
                check_fio = False
                continue
        if check_fio == False:
            print('    Error: please install fio and try again.')
            exit(0)
        else:
            print('    all ' + vm_or_compute + ' machines are installed fio, continue...')


    def is_device_mounted(self, configs):
        try:
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
                ssh.connect(hostname=configs['host'], username=configs['user'], port=configs['ssh_port'],
                            pkey=private_key)
            else:
                print('    Error: ssh connected failed, please try again.')
                exit(0)
        except Exception as e:
            print("    Error: ssh connected failed, please try again.")
            exit(0)
        stdin, stdout, stderror = ssh.exec_command('sudo lsblk -b ' + configs['dev'])
        res, err = stdout.read(), stderror.read()
        result = res if res else err
        if result.find('/') > 0 or result.find('lvm') > 0:
            self.is_umounted = False
            print("    Error: " + configs['host'] + "'s disk: " + configs['dev'] + "may hava a mounted point, please checkout again.")
        else:
            pass
        ssh.close()