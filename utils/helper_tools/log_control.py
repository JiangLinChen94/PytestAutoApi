#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2026/3/26 17:48
# @Author : alin
import logging
import os
from datetime import datetime


class LogControl:
    def __init__(self, name=__name__):
        # 日志存放目录
        self.log_path = os.path.join(os.getcwd(), "logs")
        if not os.path.exists(self.log_path):
            os.mkdir(self.log_path)

        # 日志文件名（按天生成）
        self.log_file = os.path.join(
            self.log_path,
            f"autotest_{datetime.now().strftime('%Y-%m-%d')}.log"
        )

        # 获取 logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        # 避免重复添加 handler
        if self.logger.handlers:
            self.logger.handlers.clear()

        # 日志格式
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        # 输出到文件
        file_handler = logging.FileHandler(self.log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)

        # 输出到控制台
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        # 添加处理器
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def get_logger(self):
        return self.logger


# 全局单例日志对象
logger = LogControl().get_logger()
