#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2026/3/26 14:40
# @Author : alin
import time
from utils.logging_tools.log_control import INFO, WARNING


class DelayControl:
    """
    延迟控制类，用于实现用例延迟执行功能
    """

    @staticmethod
    def delay_execution(delay_seconds: int, case_title: str):
        """
        执行延迟
        :param delay_seconds: 延迟秒数
        :param case_title: 用例标题，用于日志记录
        """
        if delay_seconds and delay_seconds > 0:
            INFO.logger.info(f"用例 '{case_title}' 开始延迟 {delay_seconds} 秒...")

            # 显示延迟进度
            for remaining in range(delay_seconds, 0, -1):
                INFO.logger.info(f"剩余延迟时间: {remaining} 秒")
                time.sleep(1)

            INFO.logger.info("延迟结束，开始执行用例")
        elif delay_seconds == 0:
            INFO.logger.info(f"用例 '{case_title}' 无延迟，立即执行")
        elif delay_seconds is None:
            # 无延迟配置，正常执行
            pass
        else:
            WARNING.logger.warning(f"无效的延迟时间: {delay_seconds} 秒，将立即执行用例")
