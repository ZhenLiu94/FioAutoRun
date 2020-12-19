# -*- coding: utf-8 -*-
import re

# 检测ip是否合法
def is_ips_illegal(ipAddrs):
    result = True
    compile_ip = re.compile(
        '^(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|[1-9])\.(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)\.(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)\.(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)$')
    for ip in ipAddrs:
        if compile_ip.match(ip):
            continue
        else:
            print('ERROR: check fio ip: ' + ip + ' False, please checkout you ip input.')
            result = False
    return result


# 检测ip是否合法
def is_ip_illegal(ipAddr):
    result = True
    compile_ip = re.compile(
        '^(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|[1-9])\.(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)\.(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)\.(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)$')
    if compile_ip.match(ipAddr):
        pass
    else:
        print('ERROR: check fio ip: ' + ipAddr + ' False, please checkout you ip input.')
        result = False
    return result



# 检测是否有重复ip，需要传入所有fio的ip地址
def is_ips_repetition(ipAddrs):
    none_repetition = list(set(ipAddrs))
    if len(ipAddrs) == len(none_repetition):
        return True
    else:
        print("ERROR: your fio testing have repetition ip, please checkout and run again。")
        return False

