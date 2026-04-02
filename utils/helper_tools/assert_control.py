#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2026/3/27 9:21
# @Author : alin
import json
import copy
import yaml
from utils.helper_tools.log_control import logger
from utils.helper_tools.common_utils import CommonUtils
from utils.mysql_tools.mysql_control import MysqlControl


class AssertControl:
    """统一断言封装"""

    def __init__(self):
        """初始化断言控制器"""
        self.mysql = MysqlControl()

    def assert_all_case(self, resp, assert_type, assert_rules, request_info=None):
        """
        统一断言入口
        :param resp: requests响应对象
        :param assert_type: 断言类型 equals / contains / not_contains / db_equals / db_contains / db_not_contains
        :param assert_rules: 断言规则 {提示信息: [预期值, 实际取值路径]}
        :param request_info: 请求信息字典，包含url, method, headers, params, json等
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
            for msg, (expect_value, actual_expr) in assert_rules.items():
                actual_value = self._get_actual_value(res, actual_expr)
                actual_str = self._to_string(actual_value)
                expect_str = self._to_string(expect_value)

                self._do_assert(assert_type, expect_str, actual_str, msg, expect_value, actual_expr, res, request_info)

        except AssertionError as e:
            # 断言失败时已经记录了详细日志，这里只重新抛出异常
            raise
        except Exception as e:
            logger.error(f"断言执行异常：{str(e)}")
            raise

    def _get_actual_value(self, resp, expr):
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

    def _to_string(self, value):
        """
        将任意类型转换为字符串，用于统一比较
        :param value: 待转换的值
        :return: 字符串格式结果
        """
        if isinstance(value, dict):
            return yaml.safe_dump(value, sort_keys=False, allow_unicode=True)
        return str(value).strip()

    def _do_assert(self, assert_type, expect_str, actual_str, msg, expect_value, actual_expr, resp, request_info=None):
        """
        根据断言类型执行断言逻辑
        :param assert_type: 断言类型
        :param expect_str: 预期字符串
        :param actual_str: 实际字符串
        :param msg: 断言失败提示信息
        :param expect_value: 原始预期值
        :param actual_expr: 实际值表达式
        :param resp: 响应对象
        :param request_info: 请求信息字典
        """
        if assert_type == "equals":
            if expect_str != actual_str:
                self._log_assert_failure(msg, expect_value, actual_expr, expect_str, actual_str, resp, request_info)
            assert expect_str == actual_str, msg

        elif assert_type == "contains":
            if expect_str not in actual_str:
                self._log_assert_failure(msg, expect_value, actual_expr, expect_str, actual_str, resp, request_info)
            assert expect_str in actual_str, msg

        elif assert_type == "not_contains":
            if expect_str in actual_str:
                self._log_assert_failure(msg, expect_value, actual_expr, expect_str, actual_str, resp, request_info)
            assert expect_str not in actual_str, msg

        elif assert_type == "db_equals":
            db_result = self._get_db_value(expect_str)
            if db_result != actual_str:
                self._log_assert_failure(msg, expect_str, actual_expr, db_result, actual_str, resp, request_info)
            assert db_result == actual_str, msg

        elif assert_type == "db_contains":
            db_result = self._get_db_value(expect_str)
            if db_result not in actual_str:
                self._log_assert_failure(msg, expect_str, actual_expr, db_result, actual_str, resp, request_info)
            assert db_result in actual_str, msg

        elif assert_type == "db_not_contains":
            db_result = self._get_db_value(expect_str)
            if db_result in actual_str:
                self._log_assert_failure(msg, expect_str, actual_expr, db_result, actual_str, resp, request_info)
            assert db_result not in actual_str, msg

        else:
            raise ValueError(f"不支持的断言类型：{assert_type}")

    def _log_assert_failure(self, msg, expect_value, actual_expr, expect_str, actual_str, resp, request_info=None):
        """
        记录断言失败的详细日志
        :param msg: 断言失败提示信息
        :param expect_value: 原始预期值
        :param actual_expr: 实际值表达式
        :param expect_str: 预期字符串
        :param actual_str: 实际字符串
        :param resp: 响应对象
        :param request_info: 请求信息字典
        """
        logger.error(f"   断言失败：{msg}")
        
        # 记录请求信息（如果提供了）
        if request_info:
            logger.error(f"   接口请求信息:")
            for key, value in request_info.items():
                if key == "headers" and isinstance(value, dict):
                    # 过滤敏感头信息
                    filtered_headers = CommonUtils.filter_sensitive_data(value, "headers")
                    logger.error(f"      {key}: {filtered_headers}")
                elif key == "json" and isinstance(value, dict):
                    # 过滤敏感JSON字段
                    filtered_json = CommonUtils.filter_sensitive_data(value, "json")
                    logger.error(f"      {key}: {filtered_json}")
                else:
                    logger.error(f"      {key}: {value}")
        
        logger.error(f"   预期值表达式: {actual_expr}")
        logger.error(f"   原始预期值: {repr(expect_value)}")
        logger.error(f"   字符串预期值: {repr(expect_str)}")
        logger.error(f"   实际获取值: {repr(actual_str)}")

        # 记录完整的响应内容
        try:
            if hasattr(resp, 'text'):
                logger.error(f"   接口完整响应:")
                logger.error(f"   {resp.text}")
            elif hasattr(resp, 'json') and isinstance(resp.json, dict):
                logger.error(f"   接口JSON响应:")
                logger.error(f"   {json.dumps(resp.json, ensure_ascii=False, indent=2)}")
        except Exception as e:
            logger.error(f"   响应内容记录失败: {str(e)}")

    def _get_db_value(self, sql):
        """
        执行SQL并返回第一个结果值
        :param sql: 待执行的SQL语句
        :return: 查询结果的第一个值
        """
        try:
            result = self.mysql.execute_sql(sql)
            return str(result[0]) if result else ""
        except Exception as e:
            logger.error(f"数据库查询失败：{sql}，错误：{str(e)}")
            return ""