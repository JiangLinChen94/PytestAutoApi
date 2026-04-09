#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2026/3/26 17:48
# @Author : alin
"""
日志装饰器，控制程序日志输入，默认为 True
如设置 False，则程序不会打印日志
"""
import ast
from functools import wraps
from utils.logging_tools.log_control import INFO, ERROR


def log_decorator(switch: bool):
    """
    封装日志装饰器, 打印请求信息
    :param switch: 定义日志开关
    :return:
    """
    def decorator(func):
        @wraps(func)
        def swapper(*args, **kwargs):

            # 判断日志为开启状态，才打印日志
            res = func(*args, **kwargs)
            # 判断日志开关为开启状态
            if switch:
                _log_msg = f"\n======================================================\n" \
                               f"用例标题: {res.detail}\n" \
                               f"请求路径: {res.url}\n" \
                               f"请求方式: {res.method}\n" \
                               f"请求头:   {res.headers}\n" \
                               f"请求内容: {res.request_body}\n" \
                               f"接口响应内容: {res.response_data}\n" \
                               f"接口响应时长: {res.res_time} ms\n" \
                               f"Http状态码: {res.status_code}\n" \
                               "====================================================="
                if res.status_code == 200:
                    INFO.logger.info(_log_msg)
                else:
                    # 失败的用例，控制台打印红色
                    ERROR.logger.error(_log_msg)
            return res
        return swapper
    return decorator
