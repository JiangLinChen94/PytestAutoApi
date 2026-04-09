#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2026/4/9 11:30
# @Author : alin
"""
断言类型枚举定义
支持多种断言方式：等于、比较、字符串、长度、包含等
"""

from enum import Enum


class AssertType(Enum):
    """断言类型枚举"""
    
    # 基础比较断言
    equals = "equals"  # 判断是否相等
    less_than = "lt"  # 判断实际结果小于预期结果
    less_than_or_equals = "le"  # 判断实际结果小于等于预期结果
    greater_than = "gt"  # 判断实际结果大于预期结果
    greater_than_or_equals = "ge"  # 判断实际结果大于等于预期结果
    not_equals = "not_eq"  # 判断实际结果不等于预期结果
    
    # 字符串断言
    string_equals = "str_eq"  # 判断字符串是否相等
    
    # 长度断言
    length_equals = "len_eq"  # 判断长度是否相等
    length_greater_than = "len_gt"  # 判断长度大于
    length_greater_than_or_equals = 'len_ge'  # 判断长度大于等于
    length_less_than = "len_lt"  # 判断长度小于
    length_less_than_or_equals = 'len_le'  # 判断长度小于等于
    
    # 包含断言
    contains = "contains"  # 判断期望结果内容包含在实际结果中
    contained_by = 'contained_by'  # 判断实际结果包含在期望结果中
    
    # 字符串匹配断言
    startswith = 'startswith'  # 检查响应内容的开头是否和预期结果内容的开头相等
    endswith = 'endswith'  # 检查响应内容的结尾是否和预期结果内容相等