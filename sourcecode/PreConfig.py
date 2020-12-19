# -*- coding: utf-8 -*-
import time
import paramiko

class PreConfig:
    def __init__(self):
        self.rbd_dict = [] #存rbd的map信息


    # 这里是跑创建文件夹的
    def create_dir(self, ssh_connects, dir_list):
        for ssh_connect in ssh_connects:
            stdin, stdout, stderr = ssh_connect.exec_command('rm -rf ' + dir_list)    # 先删除旧的
            stdin, stdout, stderr = ssh_connect.exec_command('mkdir -p ' + dir_list)  # 再创建新的


    # 这里是跑删除文件夹的，要小心，别把系统文件夹删了，慎用
    def remove_dir(self, ssh_connects, dir_list):
        for ssh_connect in ssh_connects:
            stdin, stdout, stderr = ssh_connect.exec_command('rm -rf ' + dir_list)    # 删除


    # 这里是dd写文件的，dd写一次就行
    def dd_file(self, ssh_connects, mnt, size):
        # 开始写入
        for ssh_connect in ssh_connects:
            ssh_connect.exec_command('dd if=/dev/urandom of=' + mnt + ' count='  + str(size) + ' bs=1M')
        # 检测是否写完
        while True:
            is_dd_finished = []
            is_all_finish = False
            time.sleep(5)
            for check_dd in ssh_connects:
                check_stdin, check_stdout, check_stderr = check_dd.exec_command('ps -ef|grep dd|grep /dev/urandom')
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
                break


    #如果要改rbdname那个/autofio，记得把底下del_rbd的rbdname一并改掉
    def create_and_map_rbd(self, ssh_connects, poolname, size, mnt_dir):
        for ssh_connect in ssh_connects:
            rbdname = '/autofio' + ssh_connect._host_keys._entries[0].hostnames[0]
            # 先挂载rbd
            ssh_connect.exec_command('rbd create ' + poolname + rbdname + ' --size ' + str(size) +
                                     'G;rbd feature disable ' + poolname + rbdname +
                                     ' object-map fast-diff deep-flatten;')
            time.sleep(2)
            # 然后map rbd
            rbd_stdin, rbd_stdout, rbd_stderr = ssh_connect.exec_command('rbd map ' + poolname + rbdname)
            res, err = rbd_stdout.read(), rbd_stderr.read()
            result = res if res else err
            rbd_info = str(result.decode()).strip()
            # 然后mount加格式化
            ssh_connect.exec_command('mkfs.xfs -f ' + rbd_info + ';mkdir -p ' + mnt_dir + ';mount ' + rbd_info + ' ' + mnt_dir + ';')


    # 如果要改rbdname那个/autofio，记得把底下del_rbd的rbdname一并改掉
    def del_rbd(self, ssh_connects, poolname, mnt_dir):
        for ssh_connect in ssh_connects:
            rbdname = '/autofio' + ssh_connect._host_keys._entries[0].hostnames[0]
            ssh_connect.exec_command('umount ' + mnt_dir + ';' + 'rm -rf ' + mnt_dir +
                                     ';' + 'rbd unmap ' + poolname + rbdname + ';rbd rm ' + poolname + rbdname)

