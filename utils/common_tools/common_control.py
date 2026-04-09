#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2026/4/9 11:02
# @Author : alin
import os
import json
from pathlib import Path
from typing import Text


def root_path():
    """
    获取项目根目录绝对路径
    :return: 项目根目录路径
    """
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def ensure_path_sep(path: Text) -> Text:
    """兼容 windows 和 linux 不同环境的操作系统路径 """
    if "/" in path:
        path = os.sep.join(path.split("/"))

    if "\\" in path:
        path = os.sep.join(path.split("\\"))

    return root_path() + path


def find_file_in_directory(base_dir, filename):
    """
    在目录及其子目录中递归查找文件
    :param base_dir: 基础目录
    :param filename: 文件名
    :return: 文件完整路径，未找到返回None
    """
    base_path = Path(base_dir)

    # 首先在当前目录查找
    current_path = base_path / filename
    if current_path.exists():
        return current_path

    # 递归查找子目录
    for root, dirs, files in os.walk(base_dir):
        if filename in files:
            return Path(root) / filename

    return None


def filter_sensitive_data(data, data_type="headers"):
    """
    过滤敏感信息，支持headers和json两种类型
    :param data: 原始数据
    :param data_type: 数据类型，headers或json
    :return: 过滤后的数据
    """
    if not isinstance(data, dict):
        return data

    filtered_data = data.copy()

    if data_type == "headers":
        sensitive_keys = ['Authorization', 'authorization', 'Token', 'token']
        for key in sensitive_keys:
            if key in filtered_data:
                filtered_data[key] = '***FILTERED***'

    elif data_type == "json":
        sensitive_keys = ['password', 'pwd', 'secret', 'token', 'authorization']
        for key in sensitive_keys:
            if key in filtered_data:
                filtered_data[key] = '***FILTERED***'

    return filtered_data
