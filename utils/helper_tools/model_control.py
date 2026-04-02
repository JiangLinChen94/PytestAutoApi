#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2026/3/25 19:00
# @Author : alin
from dataclasses import dataclass
from utils.helper_tools.log_control import logger


@dataclass
class CaseInfo:
    """
        规定测试用例的数据类型及是否是必填
    """
    # 必填
    feature: str
    story: str
    title: str
    request: dict
    validate: dict
    # 选填
    extract: dict = None
    parametrize: list = None
    delay: int = None  # 新增延迟字段，单位：秒
    retry: int = None  # 新增重跑字段，重跑次数
    skip: bool = None  # 新增跳过字段，是否跳过用例


def verify_yaml(case_info: dict):
    try:
        new_case = CaseInfo(**case_info)
        return new_case
    except Exception:
        logger.error("测试用例的YAML不符合框架的规范")
        raise Exception("测试用例的YAML不符合框架的规范！")