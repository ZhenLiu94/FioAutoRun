# -*- coding: utf-8 -*-
import logging
import time
import os


class LogOutput(object):
    def __init__(self):
        # 打印日志
        self.logger = logging.getLogger(__name__)
    def InfoLog(self, info):
        self.logger.setLevel(logging.INFO)
        test = logging.StreamHandler()
        formatter = logging.basicConfig(level=logging.INFO,
                    filename= '/var/log/autofio.log',
                    filemode= 'a',
                    format= '%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'
                    )
        test.setFormatter(formatter)
        self.logger.addHandler(test)
        self.logger.info(info)
    def WarningLog(self, warning):
        self.logger.setLevel(logging.WARNING)
        test = logging.StreamHandler()
        formatter = logging.basicConfig(level=logging.INFO,
                    filename= '/var/log/autofio.log',
                    filemode= 'a',
                    format= '%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'
                    )
        test.setFormatter(formatter)
        self.logger.addHandler(test)
        self.logger.warning(warning)
    def ErrorLog(self, error):
        self.logger.setLevel(logging.ERROR)
        test = logging.StreamHandler()
        formatter = logging.basicConfig(level=logging.INFO,
                    filename= '/var/log/autofio.log',
                    filemode= 'a',
                    format= '%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'
                    )
        test.setFormatter(formatter)
        self.logger.addHandler(test)
        self.logger.error(error)