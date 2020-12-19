# -*- coding: utf-8 -*-

class SpellFio:
    def __init__(self):
        pass

    #拼接全部命令
    def spell_fio(self, json_dir, ioengine, runtime, mnt, direct, fios_config):
        fio_commands = []
        for i in fios_config:
            fio_command = 'fio --filename=' + mnt + ' --ioengine='\
                          + ioengine +  ' --rw=' + str(fios_config[i]['rw'])\
                          + ' --bs=' + str(fios_config[i]['bs']) +  ' --size='\
                          + str(fios_config[i]['size']) +  ' --iodepth=' + str(fios_config[i]['iodepth'])\
                          + ' --numjobs=' + str(fios_config[i]['numjobs']) +  ' --direct=' + str(direct) \
                          + ' --runtime=' + str(runtime) + ' --name=' + str(fios_config[i]['name'])\
                          + ' --group_reporting -time_based=' + str(runtime) \
                          + ' --output-format=json --output=' + json_dir \
                          + 'bs-' + str(fios_config[i]['bs']) + '_size-' \
                          + str(fios_config[i]['size']) + '_iodepth-' + str(fios_config[i]['iodepth']) \
                          + '_numjobs-' + str(fios_config[i]['numjobs']) + '_rw-' + str(fios_config[i]['rw']) \
                          + '_runtime-' + str(runtime) + '_direct-' + str(direct) + '_ioengine-' + ioengine \
                          + '_name-' + str(fios_config[i]['name']) + '.json'
            fio_commands.append(fio_command)
        return fio_commands


    #找到测试iops和bw的
    def get_iops_bw_commands(self, fio_commands):
        fios_iops_bw_commands = []
        for fio_command in fio_commands:
            if '--name=iops_' in fio_command:
                fios_iops_bw_commands.append(fio_command)
            elif '--name=bw_' in fio_command:
                fios_iops_bw_commands.append(fio_command)
            else:
                pass
        return fios_iops_bw_commands

    #找到测试lat的
    def get_lat_commands(self, fio_commands):
        fios_lat_commands = []
        for fio_command in fio_commands:
            if '--name=lat_' in fio_command:
                fios_lat_commands.append(fio_command)
            else:
                pass
        return fios_lat_commands