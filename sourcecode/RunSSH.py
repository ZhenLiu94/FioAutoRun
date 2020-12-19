# -*- coding: utf-8 -*-
import time
import paramiko

## 五个参数分别是：
## 执行iops和bw的命令
## 执行lat的命令
## 计算节点ip及登录信息
## 虚拟机节点ip及登录信息
## 监控集群的节点ip及登录信息
class RunSSH:
    def __init__(self, fio_iops_bw, fio_lat, computes_config, vms_config, watch_config, watch_cluster_file, runtime, poolname):
        self.fio_iops_bw = fio_iops_bw # 执行iops和bw的命令
        self.fio_lat = fio_lat # 执行lat的命令
        ###############config
        self.computes_config = computes_config # 计算节点配置
        self.vms_config = vms_config # 虚拟机节点配置
        self.watch_config = watch_config # 监控节点的配置
        ###############ip
        self.compute_ips = []  # 计算节点的ip
        self.vm_ips = [] # 虚拟机节点的ip
        self.watch_ip = watch_config['host'] #监控节点的ip
        ###############connect
        self.computes_connected = [] # 计算节点已经连接上的ssh
        self.vms_connected = [] # 虚拟机几点已经连接上的ssh
        self.watch_connected = None #监控节点已经连接上的ssh
        ###############监控的两个参数
        self.watch_cluster_file = watch_cluster_file
        self.runtime = runtime
        ###############监控的池名
        self.poolname = poolname
        ##赋值
        for i in computes_config.keys():
            self.compute_ips.append(computes_config[i]['host'])
        for i in vms_config.keys():
            self.vm_ips.append(vms_config[i]['host'])


    ## 连接ssh
    def connect_ssh(self, configs):
        ssh = paramiko.SSHClient()
        know_host = paramiko.AutoAddPolicy()
        ssh.set_missing_host_key_policy(know_host)
        try:
            ssh.connect(configs['host'], configs['ssh_port'], configs['user'], configs['password'])
        except Exception as e:
            print("ssh connect has exception, please checkout your network and other config, exit.")
            exit(0)
        return ssh


    ## 连接并mount
    def connect_ssh_mount(self, configs, mnt_dir):
        ssh = paramiko.SSHClient()
        know_host = paramiko.AutoAddPolicy()
        ssh.set_missing_host_key_policy(know_host)
        try:
            ssh.connect(configs['host'], configs['ssh_port'], configs['user'], configs['password'])
            ssh.exec_command('mkdir -p ' + mnt_dir)
            ssh.exec_command('mount ' + configs['dev'] + ' ' + mnt_dir)
        except Exception as e:
            print("ssh connect has exception, please checkout your network and other config, exit.")
            exit(0)
        return ssh


    ## 断开ssh
    def close_ssh(self, ssh_connect):
        try:
            ssh_connect.close()
        except Exception as e:
            print("ssh disconnect has exception, exit.")
            exit()


    ## 断开ssh，带卸载
    def close_ssh_umount(self, ssh_connect, mnt_dir):
        try:
            ssh_connect.exec_command('rm -rf ' + mnt_dir + '/test')
            ssh_connect.exec_command('umount ' + mnt_dir)
            ssh_connect.exec_command('rm -rf ' + mnt_dir)
            ssh_connect.close()
        except Exception as e:
            print("ssh disconnect has exception, exit.")
            exit()


    ## 执行fio命令
    def run_fio_command(self, connect_configs, fio_commands):
        # 把执行fio的机器连接上
        ssh_connected = []
        for connect_config in connect_configs.keys():
            ssh_connected.append(self.connect_ssh(connect_configs[connect_config]))
        for fio in fio_commands:
            # 先执行监控
            self.watch_connected = self.connect_ssh(self.watch_config)
            stdin, stdout, stderr = self.watch_connected.exec_command(
                'temp=0;addnum=1;while true; do sleep 1; client=`ceph osd pool stats ' + self.poolname + '|grep client`; echo $client >> '
                + self.watch_cluster_file + '; temp=`expr $temp + $addnum`; if ((temp >= '
                + str(self.runtime) + '));then  break; fi; done'
            )
            # 再在所有机器上同时执行fio
            for connect in ssh_connected:
                stdin, stdout, stderr = connect.exec_command(fio)
            # 再检测是否执行完
            while True:
                is_fio_finish = []  # 判断每个fio是否停止
                is_all_finish = False  # 判断所有fio是否停止
                time.sleep(3)
                for check_fio in ssh_connected:
                    check_stdin, check_stdout, check_stderr = check_fio.exec_command('ps -ef|grep fio|grep filename')
                    res, err = check_stdout.read(), check_stderr.read()
                    result = res if res else err
                    if '--output' not in str(result.decode()):
                        is_fio_finish.append(True)
                    else:
                        is_fio_finish.append(False)
                if False in is_fio_finish:
                    print('are all machines finish (iops and bw): ' + str(is_fio_finish))
                    pass
                else:
                    is_all_finish = True  # 保证所有命令都执行完了
                    stdin, stdout, stderr = self.watch_connected.exec_command('echo ' + str(fio) + '>>' + self.watch_cluster_file)
                    self.watch_connected.close()
                    print('are all machines finish (iops and bw): ' + str(is_fio_finish))
                    break
        ## 这里一定要关掉连接哦
        for connect in ssh_connected:
            connect.close()


 ## 执行fio命令
    def run_compute_lat_command(self, connect_configs, fio_commands):
        # 把执行fio的机器连接上
        ssh_connected = []
        ssh_connected.append(self.connect_ssh(connect_configs['compute01']))
        for fio in fio_commands:
            # 先执行监控
            self.watch_connected = self.connect_ssh(self.watch_config)
            stdin, stdout, stderr = self.watch_connected.exec_command(
                'temp=0;addnum=1;while true; do sleep 1; client=`ceph osd pool stats ' + self.poolname + '|grep client`; echo $client >> '
                + self.watch_cluster_file + '; temp=`expr $temp + $addnum`; if ((temp >= '
                + str(self.runtime) + '));then  break; fi; done'
            )
            # 再在所有机器上同时执行fio
            for connect in ssh_connected:
                stdin, stdout, stderr = connect.exec_command(fio)
            # 再检测是否执行完
            while True:
                is_fio_finish = []  # 判断每个fio是否停止
                is_all_finish = False  # 判断所有fio是否停止
                time.sleep(3)
                for check_fio in ssh_connected:
                    check_stdin, check_stdout, check_stderr = check_fio.exec_command('ps -ef|grep fio|grep filename')
                    res, err = check_stdout.read(), check_stderr.read()
                    result = res if res else err
                    if '--output' not in str(result.decode()):
                        is_fio_finish.append(True)
                    else:
                        is_fio_finish.append(False)
                if False in is_fio_finish:
                    print('are all machines finish (lat): ' + str(is_fio_finish))
                    pass
                else:
                    is_all_finish = True  # 保证所有命令都执行完了
                    stdin, stdout, stderr = self.watch_connected.exec_command('echo ' + str(fio) + '>>' + self.watch_cluster_file)
                    self.watch_connected.close()
                    print('are all machines finish (lat): ' + str(is_fio_finish))
                    break
        ## 这里一定要关掉连接哦
        for connect in ssh_connected:
            connect.close()


     ## 执行fio命令
    def run_vm_lat_command(self, connect_configs, fio_commands):
        # 把执行fio的机器连接上
        ssh_connected = []
        ssh_connected.append(self.connect_ssh(connect_configs['vm01']))
        for fio in fio_commands:
            # 先执行监控
            self.watch_connected = self.connect_ssh(self.watch_config)
            stdin, stdout, stderr = self.watch_connected.exec_command(
                'temp=0;addnum=1;while true; do sleep 1; client=`ceph osd pool stats ' + self.poolname + '|grep client`; echo $client >> '
                + self.watch_cluster_file + '; temp=`expr $temp + $addnum`; if ((temp >= '
                + str(self.runtime) + '));then  break; fi; done'
            )
            # 再在所有机器上同时执行fio
            for connect in ssh_connected:
                stdin, stdout, stderr = connect.exec_command(fio)
            # 再检测是否执行完
            while True:
                is_fio_finish = []  # 判断每个fio是否停止
                is_all_finish = False  # 判断所有fio是否停止
                time.sleep(3)
                for check_fio in ssh_connected:
                    check_stdin, check_stdout, check_stderr = check_fio.exec_command('ps -ef|grep fio|grep filename')
                    res, err = check_stdout.read(), check_stderr.read()
                    result = res if res else err
                    if '--output' not in str(result.decode()):
                        is_fio_finish.append(True)
                    else:
                        is_fio_finish.append(False)
                if False in is_fio_finish:
                    print('are all machines finish (lat): ' + str(is_fio_finish))
                    pass
                else:
                    is_all_finish = True  # 保证所有命令都执行完了
                    stdin, stdout, stderr = self.watch_connected.exec_command('echo ' + str(fio) + '>>' + self.watch_cluster_file)
                    self.watch_connected.close()
                    print('are all machines finish (lat): ' + str(is_fio_finish))
                    break
        ## 这里一定要关掉连接哦
        for connect in ssh_connected:
            connect.close()























