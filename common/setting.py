#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2026/4/1 10:18
# @Author : alin
import os
from typing import Text


def root_path():
    """
    获取项目根目录绝对路径
    :return: 项目根目录路径
    """
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def ensure_path_sep(path: Text) -> Text:
    """兼容 windows 和 linux 不同环境的操作系统路径 """
    if "/" in path:
        path = os.sep.join(path.split("/"))

    if "\\" in path:
        path = os.sep.join(path.split("\\"))

    return root_path() + path
