#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2026/4/9 11:30
# @Author : alin
"""
断言控制器
统一管理多种断言类型的执行和错误处理
"""

import json
import copy
import yaml
from typing import Any, Dict, Tuple, Optional
from utils.logging_tools.log_control import ERROR, INFO
from .assert_type import AssertType
from .assert_function import AssertFunction

# 断言类型映射到函数
ASSERT_FUNCTIONS = {
    AssertType.equals: AssertFunction.equals,
    AssertType.less_than: AssertFunction.less_than,
    AssertType.less_than_or_equals: AssertFunction.less_than_or_equals,
    AssertType.greater_than: AssertFunction.greater_than,
    AssertType.greater_than_or_equals: AssertFunction.greater_than_or_equals,
    AssertType.not_equals: AssertFunction.not_equals,
    AssertType.string_equals: AssertFunction.string_equals,
    AssertType.length_equals: AssertFunction.length_equals,
    AssertType.length_greater_than: AssertFunction.length_greater_than,
    AssertType.length_greater_than_or_equals: AssertFunction.length_greater_than_or_equals,
    AssertType.length_less_than: AssertFunction.length_less_than,
    AssertType.length_less_than_or_equals: AssertFunction.length_less_than_or_equals,
    AssertType.contains: AssertFunction.contains,
    AssertType.contained_by: AssertFunction.contained_by,
    AssertType.startswith: AssertFunction.startswith,
    AssertType.endswith: AssertFunction.endswith,
}


class AssertControl:
    """统一断言控制器"""

    def __init__(self):
        """初始化断言控制器"""
        pass

    def assert_all_case(self, resp, assert_type: str, assert_rules: Dict[str, Tuple[Any, str]], 
                       request_info: Optional[Dict] = None) -> bool:
        """
        统一断言入口
        :param resp: requests响应对象
        :param assert_type: 断言类型字符串
        :param assert_rules: 断言规则 {提示信息: [预期值, 实际取值路径]}
        :param request_info: 请求信息字典
        :return: 断言是否通过
        """
        try:
            # 深拷贝响应对象，避免修改原始数据
            res = copy.deepcopy(resp)
            
            # 处理响应JSON数据
            try:
                json_data = res.json()
            except Exception:
                json_data = {"msg": "response is not json data"}
            setattr(res, "json", json_data)
            
            # 遍历所有断言规则并执行断言
            all_passed = True
            for msg, (expect_value, actual_expr) in assert_rules.items():
                try:
                    if not self._execute_single_assert(res, assert_type, expect_value, actual_expr, msg, request_info):
                        all_passed = False
                except AssertionError:
                    # 单个断言失败时，记录失败但继续执行其他断言
                    all_passed = False
            
            # 如果有任何一个断言失败，抛出异常
            if not all_passed:
                raise AssertionError("断言失败，请查看详细日志")
            
            return all_passed
            
        except AssertionError:
            # 断言失败时已经记录了详细日志，这里只重新抛出异常
            raise
        except Exception as e:
            ERROR.logger.error(f"断言执行异常：{str(e)}")
            raise

    def _execute_single_assert(self, resp, assert_type: str, expect_value: Any,
                               actual_expr: str, msg: str, request_info: Optional[Dict] = None) -> bool:
        """
        执行单个断言
        :param resp: 响应对象
        :param assert_type: 断言类型
        :param expect_value: 预期值
        :param actual_expr: 实际值表达式
        :param msg: 断言消息
        :param request_info: 请求信息
        :return: 断言是否通过
        """
        try:
            # 获取实际值
            actual_value = self._get_actual_value(resp, actual_expr)

            # 执行断言
            assert_func = self._get_assert_function(assert_type)
            if assert_func:
                result = assert_func(actual_value, expect_value)
                if result:
                    INFO.logger.info(f"断言通过：{msg}")
                    return True
                else:
                    self._log_assert_failure(msg, expect_value, actual_expr, actual_value, resp, request_info)
                    # 断言失败时抛出 AssertionError，让 pytest 能够捕获并标记测试失败
                    raise AssertionError(f"断言失败：{msg}")
            else:
                ERROR.logger.error(f"不支持的断言类型：{assert_type}")
                raise AssertionError(f"不支持的断言类型：{assert_type}")

        except AssertionError:
            # 重新抛出 AssertionError
            raise
        except Exception as e:
            ERROR.logger.error(f"断言执行异常：{msg}, 错误：{str(e)}")
            raise AssertionError(f"断言执行异常：{msg}, 错误：{str(e)}")

    def _get_assert_function(self, assert_type: str):
        """获取断言函数"""
        try:
            assert_enum = AssertType(assert_type)
            return ASSERT_FUNCTIONS.get(assert_enum)
        except ValueError:
            return None

    def _get_actual_value(self, resp, expr: str) -> Any:
        """
        根据表达式获取实际值
        :param resp: 响应对象
        :param expr: 取值表达式
        :return: 实际值
        """
        try:
            # 如果表达式是响应对象的属性，直接获取
            if hasattr(resp, expr):
                return getattr(resp, expr)

            # 如果表达式是JSON路径，使用JSONPath解析
            if expr.startswith("$"):
                import jsonpath
                json_data = getattr(resp, "json", {})
                result = jsonpath.jsonpath(dict(json_data), expr)
                return result[0] if result else None

            # 如果表达式是JSON字段名，从JSON数据中提取
            json_data = getattr(resp, "json", {})
            if isinstance(json_data, dict) and expr in json_data:
                return json_data.get(expr)

            # 默认返回表达式本身
            return expr

        except Exception:
            return expr

    def _log_assert_failure(self, msg: str, expect_value: Any, actual_expr: str,
                            actual_value: Any, resp, request_info: Optional[Dict] = None):
        """
        记录断言失败的详细日志
        :param msg: 断言失败提示信息
        :param expect_value: 原始预期值
        :param actual_expr: 实际值表达式
        :param actual_value: 实际值
        :param resp: 响应对象
        :param request_info: 请求信息字典
        """
        ERROR.logger.error(f"断言失败：{msg}")

        # 记录请求信息（如果提供了）
        if request_info:
            ERROR.logger.error(f"接口请求信息:")
            for key, value in request_info.items():
                if key == "headers" and isinstance(value, dict):
                    # 过滤敏感头信息
                    filtered_headers = self._filter_sensitive_data(value, "headers")
                    ERROR.logger.error(f"      {key}: {filtered_headers}")
                elif key == "json" and isinstance(value, dict):
                    # 过滤敏感JSON字段
                    filtered_json = self._filter_sensitive_data(value, "json")
                    ERROR.logger.error(f"      {key}: {filtered_json}")
                else:
                    ERROR.logger.error(f"      {key}: {value}")

        ERROR.logger.error(f"预期值表达式: {actual_expr}")
        ERROR.logger.error(f"原始预期值: {repr(expect_value)}")
        ERROR.logger.error(f"实际获取值: {repr(actual_value)}")

        # 记录完整的响应内容
        try:
            if hasattr(resp, 'text'):
                ERROR.logger.error(f"接口完整响应:")
                ERROR.logger.error(f"{resp.text}")
            elif hasattr(resp, 'json') and isinstance(resp.json, dict):
                ERROR.logger.error(f"接口JSON响应:")
                ERROR.logger.error(f"{json.dumps(resp.json, ensure_ascii=False, indent=2)}")
        except Exception as e:
            ERROR.logger.error(f"   响应内容记录失败: {str(e)}")

    def _filter_sensitive_data(self, data: Dict, data_type: str) -> Dict:
        """过滤敏感数据"""
        filtered_data = data.copy()

        if data_type == "headers":
            sensitive_keys = ['authorization', 'token', 'password', 'secret']
            for key in sensitive_keys:
                if key.lower() in [k.lower() for k in filtered_data.keys()]:
                    for original_key in filtered_data.keys():
                        if original_key.lower() == key.lower():
                            filtered_data[original_key] = "***FILTERED***"

        elif data_type == "json":
            sensitive_keys = ['password', 'token', 'secret', 'authorization']
            for key in sensitive_keys:
                if key in filtered_data:
                    filtered_data[key] = "***FILTERED***"

        return filtered_data


# 便捷断言函数
def assert_equals(actual: Any, expected: Any, msg: str = "") -> bool:
    """等于断言便捷函数"""
    return AssertFunction.equals(actual, expected)


def assert_less_than(actual: Any, expected: Any, msg: str = "") -> bool:
    """小于断言便捷函数"""
    return AssertFunction.less_than(actual, expected)


def assert_greater_than(actual: Any, expected: Any, msg: str = "") -> bool:
    """大于断言便捷函数"""
    return AssertFunction.greater_than(actual, expected)


def assert_contains(actual: Any, expected: Any, msg: str = "") -> bool:
    """包含断言便捷函数"""
    return AssertFunction.contains(actual, expected)


def assert_startswith(actual: Any, expected: Any, msg: str = "") -> bool:
    """开头匹配断言便捷函数"""
    return AssertFunction.startswith(actual, expected)


def assert_endswith(actual: Any, expected: Any, msg: str = "") -> bool:
    """结尾匹配断言便捷函数"""
    return AssertFunction.endswith(actual, expected)
