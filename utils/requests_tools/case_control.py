#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2026/3/26 15:10
# @Author : alin
from utils.logging_tools.log_control import INFO

from utils.helper_tools.extract_control import ExtractControl
from utils.helper_tools.model_control import CaseInfo
from utils.helper_tools.delay_control import DelayControl
from utils.helper_tools.retry_control import RetryControl
from utils.helper_tools.skip_control import SkipControl
from utils.requests_tools.request_control import RequestsControl
from utils.helper_tools.assert_control import AssertControl


def _execute_single_case(case_info: CaseInfo):
    """
    执行单个用例（不包含重跑逻辑）
    :param case_info: 用例信息
    """
    # 检查是否跳过用例
    SkipControl.check_and_skip(case_info.skip, case_info)
    
    # 日志
    INFO.logger.info(
        f"接口信息：{case_info.feature} >> {case_info.story} >> {case_info.title}"
    )
    
    # 执行延迟（如果有配置）
    DelayControl.delay_execution(case_info.delay, case_info.title)
    
    # 发送请求
    request_params = ExtractControl().change(case_info.request)
    resp = RequestsControl().send_all_request(**request_params)
    
    # 请求之后：提取值
    if case_info.extract:
        for ex_key, ex_value in case_info.extract.items():
            ExtractControl().extract(ex_key, resp, *ex_value)
    
    # 断言（传递请求信息用于失败时打印）
    if case_info.validate:
        for assert_key, assert_value in ExtractControl().change(case_info.validate).items():
            AssertControl().assert_all_case(resp, assert_key, assert_value, request_params)
    
    return resp


def use_case_execution(case_info: CaseInfo):
    """
    用例执行入口，包含重跑逻辑
    :param case_info: 用例信息
    """
    # 使用重跑控制执行用例
    return RetryControl.execute_with_retry(_execute_single_case, case_info, case_info.retry)