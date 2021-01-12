# -*- coding: utf-8 -*-

import sys
from sourcecode.LoadYaml import *
from sourcecode.SpellFio import *
from sourcecode.DetectionConfig import *
from sourcecode.RunSSH import *
from sourcecode.PreConfig import *
from sourcecode.GetResult import *
from sourcecode.DoExcel import *
from sourcecode.LogOutput import *

####################################
###单独解析excel
save_path = r"C:/Users/liiuzhen/Desktop/"
xlsx_name = "autotest_vm"
workbook = DoExcel(save_path + xlsx_name + '.xlsx', xlsx_name)
folder_name = workbook.get_location('compute')
fio_path = r"C:/Users/liiuzhen/Desktop/autofiooutput2021-01-09-16-37-53/vm/"
ceph_s_path = r"C:/Users/liiuzhen/Desktop/autofiooutput2021-01-09-16-37-53/ceph_s/vm/"
#取数据
lat_data, iops_bw_data = workbook.parse_json(fio_path, ceph_s_path)
workbook.to_excel(lat_data, iops_bw_data, 4)
workbook.workbook.close()