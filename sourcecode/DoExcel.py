# -*- coding: utf-8 -*-

import xlsxwriter
import json
import os
import sys
import math

reload(sys)
sys.setdefaultencoding('utf8')

class DoExcel:
    fio_dir = 0
    ceph_s_dir = 0
    workbook = 0
    worksheet = 0
    style0 = 0
    style1 = 0
    style2 = 0
    #初始化创建表格
    def __init__(self, workbook_name, worhsheet_name):
        DoExcel.workbook = xlsxwriter.Workbook(workbook_name)
        DoExcel.worksheet = DoExcel.workbook.add_worksheet(worhsheet_name)
        DoExcel.style0 = DoExcel.workbook.add_format({
            "align": "center",
        })

        DoExcel.style1 = DoExcel.workbook.add_format({
            "fg_color": '#00FF7F',  # 单元格的背景颜色
            "align": "center",  # 对齐方式
            "valign": "vcenter",  # 字体对齐方式
        })

        DoExcel.style2 = DoExcel.workbook.add_format({
            "fg_color": '#38B0DE',  # 单元格的背景颜色
            "align": "center",  # 对齐方式
            "valign": "vcenter",  # 字体对齐方式
        })
        # 设置表宽
        DoExcel.worksheet.set_column('A:A', 10)
        DoExcel.worksheet.set_column('B:B', 7)
        DoExcel.worksheet.set_column('C:C', 7)
        DoExcel.worksheet.set_column('D:D', 9)
        DoExcel.worksheet.set_column('E:E', 9)
        DoExcel.worksheet.set_column('F:F', 11)
        DoExcel.worksheet.set_column('G:G', 9)
        DoExcel.worksheet.set_column('H:H', 8)
        DoExcel.worksheet.set_column('I:I', 10)
        DoExcel.worksheet.set_column('J:J', 17)
        DoExcel.worksheet.set_column('K:K', 17)
        DoExcel.worksheet.set_column('L:L', 17)
        DoExcel.worksheet.set_column('M:M', 17)
        DoExcel.worksheet.set_column('N:N', 17)
        DoExcel.worksheet.set_column('O:O', 17)
        DoExcel.worksheet.set_column('P:P', 17)
        DoExcel.worksheet.set_column('Q:Q', 17)#放ceph -s 写
        DoExcel.worksheet.set_column('R:R', 17)#放ceph -s 读

        # 设置表头
        DoExcel.worksheet.write(0, 0, '机器数量', DoExcel.style1)
        DoExcel.worksheet.write(0, 1, 'bw', DoExcel.style1)
        DoExcel.worksheet.write(0, 2, 'size', DoExcel.style1)
        DoExcel.worksheet.write(0, 3, 'iodepth', DoExcel.style1)
        DoExcel.worksheet.write(0, 4, 'numjobs', DoExcel.style1)
        DoExcel.worksheet.write(0, 5, 'rw', DoExcel.style1)
        DoExcel.worksheet.write(0, 6, 'runtime', DoExcel.style1)
        DoExcel.worksheet.write(0, 7, 'direct', DoExcel.style1)
        DoExcel.worksheet.write(0, 8, 'ioengine', DoExcel.style1)
        DoExcel.worksheet.write(0, 9, 'name', DoExcel.style1)
        DoExcel.worksheet.write(0, 10, 'iops_write(op/s)', DoExcel.style2)
        DoExcel.worksheet.write(0, 11, 'iops_read(op/s)', DoExcel.style2)
        DoExcel.worksheet.write(0, 12, 'bw_write(MB/s)', DoExcel.style2)
        DoExcel.worksheet.write(0, 13, 'bw_read(MB/s)', DoExcel.style2)
        DoExcel.worksheet.write(0, 14, 'lat_write(ms)', DoExcel.style2)
        DoExcel.worksheet.write(0, 15, 'lat_read(ms)', DoExcel.style2)
        DoExcel.worksheet.write(0, 16, '集群iops_写(op/s)', DoExcel.style2)
        DoExcel.worksheet.write(0, 17, '集群iops_读(op/s)', DoExcel.style2)


    # 处理ceph_s的原始数据，参数只能填是wr还是rd
    def parse_ceph_s(self, ceph_s_dir, wr_or_rd):
        all_list_fio = []
        iops_list = []
        averages = []
        upperlimit = 0
        lowerlimit = 0
        iops_num = 0
        sum = 0
        max_num = 0.0
        min_num = 99999999999.9

        for root, dirs, files in os.walk(ceph_s_dir):
            for file in files:
                if file.find("data") < 0:
                    continue
                f = open(os.path.join(root, file), "r")
                for line in f:
                    all_list_fio.append(line.strip('\n'))
            f.close()

        for i in range(len(all_list_fio)):
            if len(all_list_fio[i]) == 0:
                continue
            if 'filename' in all_list_fio[i]:
                if len(iops_list):
                    upperlimit = int(math.ceil(len(iops_list)*0.9))
                    lowerlimit = int(math.ceil(len(iops_list)*0.2))
                    iops_num = upperlimit - lowerlimit
                    for j in range(lowerlimit, upperlimit):
                        sum += iops_list[j]
                        if max_num <= iops_list[j]:
                            max_num = iops_list[j]
                        elif (min_num >= iops_list[j]) and (iops_list[j] > 0.1):
                            min_num = iops_list[j]
                iops_list = []
                sum = sum - min_num - max_num
                averages.append(str(round(sum / (iops_num - 2), 2)) + ':' + all_list_fio[i].split('/')[-1])
                sum = 0
                max_num = 0
                min_num = 9999999999.9
                continue
            else:
                if wr_or_rd == 'wr':
                    iops = all_list_fio[i].split(',')[-1]
                elif wr_or_rd == 'rd':
                    iops = all_list_fio[i].split(',')[-2]
                iops = iops.split('op/s')[0]
                if 'k' in iops:
                    iops = float(iops.split('k')[0])
                    iops = iops * 1024
                iops = round(float(iops), 2)
                iops_list.append(iops)
        return averages


    #解析json数据
    def parse_json(self, root_dir, ceph_s_dir):
        #直接把ceph-s的数据取过来，现在是两个list，需要弄成字典
        ceph_s_wr_list = self.parse_ceph_s(ceph_s_dir, 'wr')
        ceph_s_rd_list = self.parse_ceph_s(ceph_s_dir, 'rd')
        #把数据存成字典，Key和json的结构一样，value就是值
        ceph_s_wr = {}
        ceph_s_rd = {}
        for wr in ceph_s_wr_list:
            ceph_s_wr[wr.split(":")[-1]] = wr.split(":")[0]
        for rd in ceph_s_rd_list:
            ceph_s_rd[rd.split(":")[-1]] = rd.split(":")[0]

        ## 取文件夹下目录
        folder_list = os.listdir(root_dir)
        for folder in folder_list:
            if os.path.isfile(os.path.join(root_dir, folder)):
                dbtype_list.remove(folder)

        ## 拼成整个目录
        file_dir_list = []
        for folder in folder_list:
            file_dir_list.append(root_dir + folder)

        ##取目录下所有文件
        ## all_data的结构：
        ## 按照文件夹取ip，作为最外层key；
        ## 按照每个文件夹内的文件名，取内层key；
        ## 取数据，就是value
        all_data = {}
        files_dict = {}
        for file_dir in file_dir_list:
            for root, dirs, files in os.walk(file_dir):
                # print(root) #当前目录路径
                # print(dirs) #当前路径下所有子目录
                # print(files) #当前路径下所有非目录子文件
                for file in files:
                    ##取配置
                    values = file.split('_')
                    bs = values[0].split('-')[-1]
                    size = values[1].split('-')[-1]
                    iodepth = values[2].split('-')[-1]
                    numjobs = values[3].split('-')[-1]
                    rw = values[4].split('-')[-1]
                    runtime = values[5].split('-')[-1]
                    direct = values[6].split('-')[-1]
                    ioengine = values[7].split('-')[-1]
                    name = values[8].split('-')[-1] + '_' + values[9].split('.')[0]
                    ##取json数据
                    with open(root + '/' + file, "r") as f:
                        data = json.loads(f.read())
                        write_iops = str(data["jobs"][0]["write"]["iops"])
                        read_iops = str(data["jobs"][0]["read"]["iops"])
                        write_bw = str(data["jobs"][0]["write"]["bw"])
                        read_bw = str(data["jobs"][0]["read"]["bw"])
                        write_lat = str(data["jobs"][0]["write"]["lat"]["mean"])
                        read_lat = str(data["jobs"][0]["read"]["lat"]["mean"])
                    f.close()
                    files_dict[file] = [bs, size, iodepth, numjobs, rw, runtime, direct, ioengine, name, write_iops,
                                        read_iops, write_bw, read_bw, write_lat, read_lat]
                all_data[root.split('/')[-1]] = files_dict

        machine_num = len(all_data)  ##机器数量

        ##把时延的单独拿出来
        all_lat_data = {}  # 时延数据
        all_iops_bw_data = {}  # iops和bw数据
        for ip in all_data.keys():
            for data in all_data[ip].keys():
                if data.find('lat_') > 0:
                    all_lat_data[data] = all_data[ip][data]
                    all_data[ip].pop(data)
                else:
                    continue

        ##所有fio命令（只是iops和bw的）
        fio_iops_bw_commands = []
        all_iops_bw_sum_data = {}
        ##把iops和吞吐的单独拿出来
        all_iops_bw_data = all_data  # iops和bw数据
        ## 如果只有一台机器测试iops和bw，那么就只取这一台的值
        if len(all_iops_bw_data) == 1:
            all_iops_bw_data = all_iops_bw_data.values()[0]
        ##大于一台则把iops和bw的加在一起
        else:
            # 先把命令的key取出来
            for iops_bw_data in all_iops_bw_data.keys():
                fio_iops_bw_commands = all_iops_bw_data[iops_bw_data].keys()
                break
            for command in fio_iops_bw_commands:
                all_iops_bw_sum_data[command] = [None, None, None, None, None, None, None, None, None, '0', '0', '0',
                                                 '0', '0', '0']
            ##根据命令，遍历每台机器的数据
            for data in all_iops_bw_sum_data.keys():  # fio命令以及空数据
                for ip in all_iops_bw_data.keys():  # 所有机器ip
                    for key in all_iops_bw_data[ip].keys():
                        if key == data:
                            # 取配置
                            all_iops_bw_sum_data[data][0] = all_iops_bw_data[ip][key][0]  # bs
                            all_iops_bw_sum_data[data][1] = all_iops_bw_data[ip][key][1]  # size
                            all_iops_bw_sum_data[data][2] = all_iops_bw_data[ip][key][2]  # iodepth
                            all_iops_bw_sum_data[data][3] = all_iops_bw_data[ip][key][3]  # numjobs
                            all_iops_bw_sum_data[data][4] = all_iops_bw_data[ip][key][4]  # rw
                            all_iops_bw_sum_data[data][5] = all_iops_bw_data[ip][key][5]  # runtime
                            all_iops_bw_sum_data[data][6] = all_iops_bw_data[ip][key][6]  # direct
                            all_iops_bw_sum_data[data][7] = all_iops_bw_data[ip][key][7]  # ioengine
                            all_iops_bw_sum_data[data][8] = all_iops_bw_data[ip][key][8]  # name
                            # 加数据
                            all_iops_bw_sum_data[data][9] = all_iops_bw_sum_data[data][9] + '+' + \
                                                            all_iops_bw_data[ip][key][9]
                            all_iops_bw_sum_data[data][10] = all_iops_bw_sum_data[data][10] + '+' + \
                                                             all_iops_bw_data[ip][key][10]
                            all_iops_bw_sum_data[data][11] = all_iops_bw_sum_data[data][11] + '+' + \
                                                             all_iops_bw_data[ip][key][11]
                            all_iops_bw_sum_data[data][12] = all_iops_bw_sum_data[data][12] + '+' + \
                                                             all_iops_bw_data[ip][key][12]
                            all_iops_bw_sum_data[data][13] = all_iops_bw_sum_data[data][13] + '+' + \
                                                             all_iops_bw_data[ip][key][13]
                            all_iops_bw_sum_data[data][14] = all_iops_bw_sum_data[data][14] + '+' + \
                                                             all_iops_bw_data[ip][key][14]

        # all_lat_data #这个是lat的
        # all_iops_bw_sum_data #这个是iops和bw的
        # 这里把ceph -s的监控也加上了
        for lat_data in all_lat_data.keys():
            for wr in ceph_s_wr.keys():
                if lat_data == wr:
                    all_lat_data[lat_data].append(ceph_s_wr[wr])
            for rd in ceph_s_rd.keys():
                if lat_data == rd:
                    all_lat_data[lat_data].append(ceph_s_rd[rd])

        for iops_bw_sum_data in all_iops_bw_sum_data.keys():
            for wr in ceph_s_wr.keys():
                if iops_bw_sum_data == wr:
                    all_iops_bw_sum_data[iops_bw_sum_data].append(ceph_s_wr[wr])
            for rd in ceph_s_rd.keys():
                if iops_bw_sum_data == rd:
                    all_iops_bw_sum_data[iops_bw_sum_data].append(ceph_s_rd[rd])
        return all_lat_data, all_iops_bw_sum_data


    #转换成excel，两个averages参数是集群监控的，分为读和写
    def to_excel(self, all_lat_data, all_iops_bw_sum_data, iops_bw_machines_num):
        count = 1 #从第几行开始填，因为0是表头了，所以从1开始
        #填写时延
        for fio_command in all_lat_data.keys():
            #填参数开始
            DoExcel.worksheet.write(count, 0, '1', DoExcel.style0)#时延只有一台
            DoExcel.worksheet.write(count, 1, str(all_lat_data[fio_command][0]), DoExcel.style0)
            DoExcel.worksheet.write(count, 2, str(all_lat_data[fio_command][1]), DoExcel.style0)
            DoExcel.worksheet.write(count, 3, str(all_lat_data[fio_command][2]), DoExcel.style0)
            DoExcel.worksheet.write(count, 4, str(all_lat_data[fio_command][3]), DoExcel.style0)
            DoExcel.worksheet.write(count, 5, str(all_lat_data[fio_command][4]), DoExcel.style0)
            DoExcel.worksheet.write(count, 6, str(all_lat_data[fio_command][5]), DoExcel.style0)
            DoExcel.worksheet.write(count, 7, str(all_lat_data[fio_command][6]), DoExcel.style0)
            DoExcel.worksheet.write(count, 8, str(all_lat_data[fio_command][7]), DoExcel.style0)
            DoExcel.worksheet.write(count, 9, str(all_lat_data[fio_command][8]), DoExcel.style0)
            DoExcel.worksheet.write(count, 10, '---', DoExcel.style0)
            DoExcel.worksheet.write(count, 11, '---', DoExcel.style0)
            DoExcel.worksheet.write(count, 12, '---', DoExcel.style0)
            DoExcel.worksheet.write(count, 13, '---', DoExcel.style0)
            #如果是读的，只取读时延
            if str(all_lat_data[fio_command][4]).find('read') >= 0:
                DoExcel.worksheet.write(count, 14, '---', DoExcel.style0)
                DoExcel.worksheet.write(count, 15, str(all_lat_data[fio_command][14]), DoExcel.style0)
            #如果是写的，只取写时延
            elif str(all_lat_data[fio_command][4]).find('write') >= 0:
                DoExcel.worksheet.write(count, 14, str(all_lat_data[fio_command][13]), DoExcel.style0)
                DoExcel.worksheet.write(count, 15, '---', DoExcel.style0)
            else:
                DoExcel.worksheet.write(count, 14, 'has wrong', DoExcel.style0)
                DoExcel.worksheet.write(count, 15, 'has wrong', DoExcel.style0)
            DoExcel.worksheet.write(count, 16, str(all_lat_data[fio_command][15]), DoExcel.style0)
            DoExcel.worksheet.write(count, 17, str(all_lat_data[fio_command][16]), DoExcel.style0)
            count = count + 1
        # 填写iops和bw
        for fio_command in all_iops_bw_sum_data.keys():
            # 填参数开始
            DoExcel.worksheet.write(count, 0, iops_bw_machines_num, DoExcel.style0)  # 机器数量自己制定
            DoExcel.worksheet.write(count, 1, str(all_iops_bw_sum_data[fio_command][0]), DoExcel.style0)
            DoExcel.worksheet.write(count, 2, str(all_iops_bw_sum_data[fio_command][1]), DoExcel.style0)
            DoExcel.worksheet.write(count, 3, str(all_iops_bw_sum_data[fio_command][2]), DoExcel.style0)
            DoExcel.worksheet.write(count, 4, str(all_iops_bw_sum_data[fio_command][3]), DoExcel.style0)
            DoExcel.worksheet.write(count, 5, str(all_iops_bw_sum_data[fio_command][4]), DoExcel.style0)
            DoExcel.worksheet.write(count, 6, str(all_iops_bw_sum_data[fio_command][5]), DoExcel.style0)
            DoExcel.worksheet.write(count, 7, str(all_iops_bw_sum_data[fio_command][6]), DoExcel.style0)
            DoExcel.worksheet.write(count, 8, str(all_iops_bw_sum_data[fio_command][7]), DoExcel.style0)
            DoExcel.worksheet.write(count, 9, str(all_iops_bw_sum_data[fio_command][8]), DoExcel.style0)
            # 如果是读的，只取读iops
            if str(all_iops_bw_sum_data[fio_command][4]).find('read') >= 0:
                DoExcel.worksheet.write(count, 10, '---', DoExcel.style0)
                DoExcel.worksheet.write(count, 11, '=ROUND(SUM('  + str(all_iops_bw_sum_data[fio_command][10]) + '),2)', DoExcel.style0)
            # 如果是写的，只取写iops
            elif str(all_iops_bw_sum_data[fio_command][4]).find('write') >= 0:
                DoExcel.worksheet.write(count, 10, '=ROUND(SUM('  + str(all_iops_bw_sum_data[fio_command][9]) + '),2)', DoExcel.style0)
                DoExcel.worksheet.write(count, 11, '---', DoExcel.style0)
            else:
                DoExcel.worksheet.write(count, 10, 'has wrong', DoExcel.style0)
                DoExcel.worksheet.write(count, 11, 'has wrong', DoExcel.style0)
            # 如果是读的，只取读bw
            if str(all_iops_bw_sum_data[fio_command][4]).find('read') >= 0:
                DoExcel.worksheet.write(count, 12, '---', DoExcel.style0)
                DoExcel.worksheet.write(count, 13, '=ROUND(SUM('  + str(all_iops_bw_sum_data[fio_command][12]) + '),2)', DoExcel.style0)
            # 如果是写的，只取写bw
            elif str(all_iops_bw_sum_data[fio_command][4]).find('write') >= 0:
                DoExcel.worksheet.write(count, 12, '=ROUND(SUM('  + str(all_iops_bw_sum_data[fio_command][11]) + '),2)', DoExcel.style0)
                DoExcel.worksheet.write(count, 13, '---', DoExcel.style0)
            else:
                DoExcel.worksheet.write(count, 14, 'has wrong', DoExcel.style0)
                DoExcel.worksheet.write(count, 15, 'has wrong', DoExcel.style0)
            DoExcel.worksheet.write(count, 14, '---', DoExcel.style0)
            DoExcel.worksheet.write(count, 15, '---', DoExcel.style0)
            DoExcel.worksheet.write(count, 16, str(all_iops_bw_sum_data[fio_command][15]), DoExcel.style0)
            DoExcel.worksheet.write(count, 17, str(all_iops_bw_sum_data[fio_command][16]), DoExcel.style0)
            count = count + 1

if __name__ == '__main__':
    #################################代填参数 start###################################################
    ## 在指定名字的时候，如果小于10，要写成02，05这样的形式
    ##生成excel的文件名，不用加后缀
    xlsx_name = "autotest"
    ##生成excelsheet的名字
    sheet_name = ""
    ## fio数据路径
    fio_path = "C:/Users/liiuzhen/Desktop/fioformat/autofiooutput2020-12-18-13-02-35/compute/"
    ## ceph-s数据路径
    ceph_s_path = r"C:/Users/liiuzhen/Desktop/fioformat/autofiooutput2020-12-18-13-02-35/ceph_s/compute/"
    ## 生成excel所在路径
    save_path = r"D:/"
    #################################代填参数 end#####################################################

    workbook = DoExcel(save_path + xlsx_name + '.xlsx', sheet_name)
    # averages_rd = workbook.parse_ceph_s(ceph_s_path, 'rd')
    # averages_wr = workbook.parse_ceph_s(ceph_s_path, 'wr')
    lat_data, iops_bw_data = workbook.parse_json(fio_path, ceph_s_path)
    workbook.to_excel(lat_data, iops_bw_data, 3)
    workbook.workbook.close()


































