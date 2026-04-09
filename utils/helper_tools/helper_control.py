#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2026/3/26 14:50
# @Author : alin
import time
import os
from utils.file_tools.yaml_control import YamlControl
from utils.file_tools.config_control import config


class HelperControl:
    @staticmethod
    def read_extract(key):
        """
        根据key值读取extract关联文件中的value值
        :param key: 需要读取的键
        :return:
        """
        return YamlControl.read_extract_by_key(key)

    @staticmethod
    def get_random_number():
        """
        获取随机数
        :return:
        """
        return str(int(time.time()))

    @staticmethod
    def get_env():
        """
        获取接口运行环境
        :return: 返回配置文件中env,base_url地址
        """
        return config.get("env", "base_url")

    @staticmethod
    def get_project_root():
        """
        获取项目根目录绝对路径
        :return: 项目根目录路径
        """
        return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


if __name__ == '__main__':
    print(HelperControl().read_extract('token'))
    print(HelperControl().get_project_root())
