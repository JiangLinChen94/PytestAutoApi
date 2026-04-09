#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2026/4/9 11:30
# @Author : alin
"""
断言函数实现
包含所有断言类型的实现逻辑
"""

from typing import Any


class AssertFunction:
    """断言函数实现类"""
    
    @staticmethod
    def equals(actual: Any, expected: Any) -> bool:
        """判断是否相等"""
        return str(actual).strip() == str(expected).strip()
    
    @staticmethod
    def less_than(actual: Any, expected: Any) -> bool:
        """判断实际结果小于预期结果"""
        try:
            return float(actual) < float(expected)
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def less_than_or_equals(actual: Any, expected: Any) -> bool:
        """判断实际结果小于等于预期结果"""
        try:
            return float(actual) <= float(expected)
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def greater_than(actual: Any, expected: Any) -> bool:
        """判断实际结果大于预期结果"""
        try:
            return float(actual) > float(expected)
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def greater_than_or_equals(actual: Any, expected: Any) -> bool:
        """判断实际结果大于等于预期结果"""
        try:
            return float(actual) >= float(expected)
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def not_equals(actual: Any, expected: Any) -> bool:
        """判断实际结果不等于预期结果"""
        return not AssertFunction.equals(actual, expected)
    
    @staticmethod
    def string_equals(actual: Any, expected: Any) -> bool:
        """判断字符串是否相等（严格字符串比较）"""
        return str(actual) == str(expected)
    
    @staticmethod
    def length_equals(actual: Any, expected: Any) -> bool:
        """判断长度是否相等"""
        try:
            return len(str(actual)) == int(expected)
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def length_greater_than(actual: Any, expected: Any) -> bool:
        """判断长度大于"""
        try:
            return len(str(actual)) > int(expected)
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def length_greater_than_or_equals(actual: Any, expected: Any) -> bool:
        """判断长度大于等于"""
        try:
            return len(str(actual)) >= int(expected)
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def length_less_than(actual: Any, expected: Any) -> bool:
        """判断长度小于"""
        try:
            return len(str(actual)) < int(expected)
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def length_less_than_or_equals(actual: Any, expected: Any) -> bool:
        """判断长度小于等于"""
        try:
            return len(str(actual)) <= int(expected)
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def contains(actual: Any, expected: Any) -> bool:
        """判断期望结果内容包含在实际结果中"""
        return str(expected) in str(actual)
    
    @staticmethod
    def contained_by(actual: Any, expected: Any) -> bool:
        """判断实际结果包含在期望结果中"""
        return str(actual) in str(expected)
    
    @staticmethod
    def startswith(actual: Any, expected: Any) -> bool:
        """检查响应内容的开头是否和预期结果内容的开头相等"""
        return str(actual).startswith(str(expected))
    
    @staticmethod
    def endswith(actual: Any, expected: Any) -> bool:
        """检查响应内容的结尾是否和预期结果内容相等"""
        return str(actual).endswith(str(expected))