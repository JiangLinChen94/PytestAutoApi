#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2026/4/1 14:19
# @Author : alin
import pytest
from utils.helper_tools.log_control import logger


class SkipControl:
    """
    跳过控制类，用于实现用例跳过功能
    """

    @staticmethod
    def check_and_skip(skip_flag: bool, case_info):
        """
        检查并跳过用例
        :param skip_flag: 跳过标志
        :param case_info: 用例信息
        """
        if skip_flag is True:
            logger.warning(f"⏭️ 用例 '{case_info.title}' 被标记为跳过，跳过执行")
            pytest.skip(f"用例 '{case_info.title}' 被标记为跳过")
        elif skip_flag is False:
            logger.info(f"✅ 用例 '{case_info.title}' 正常执行")
        # skip_flag为None时，正常执行

    @staticmethod
    def skip_with_reason(reason: str, case_info):
        """
        带原因的跳过用例
        :param reason: 跳过原因
        :param case_info: 用例信息
        """
        logger.warning(f"⏭️ 用例 '{case_info.title}' 被跳过，原因: {reason}")
        pytest.skip(f"用例 '{case_info.title}' 被跳过，原因: {reason}")

    @staticmethod
    def conditional_skip(condition: bool, reason: str, case_info):
        """
        条件跳过用例
        :param condition: 跳过条件
        :param reason: 跳过原因
        :param case_info: 用例信息
        """
        if condition:
            SkipControl.skip_with_reason(reason, case_info)

    @staticmethod
    def skip_if_env_not_set(env_var: str, case_info):
        """
        环境变量未设置时跳过用例
        :param env_var: 环境变量名
        :param case_info: 用例信息
        """
        import os
        if not os.getenv(env_var):
            SkipControl.skip_with_reason(f"环境变量 {env_var} 未设置", case_info)

    @staticmethod
    def skip_if_condition_true(condition_func, reason: str, case_info):
        """
        条件满足时跳过用例
        :param condition_func: 条件判断函数
        :param reason: 跳过原因
        :param case_info: 用例信息
        """
        if condition_func():
            SkipControl.skip_with_reason(reason, case_info)