#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2026/4/1 17:10
# @Author : alin
import os
import yaml
import json
from pathlib import Path

from utils.logging_tools.log_control import INFO


class CommonUtils:
    """通用工具类，包含项目中常用的重复代码逻辑"""

    @staticmethod
    def find_file_in_directory(base_dir, filename):
        """
        在目录及其子目录中递归查找文件
        :param base_dir: 基础目录
        :param filename: 文件名
        :return: 文件完整路径，未找到返回None
        """
        base_path = Path(base_dir)

        # 首先在当前目录查找
        current_path = base_path / filename
        if current_path.exists():
            return current_path

        # 递归查找子目录
        for root, dirs, files in os.walk(base_dir):
            if filename in files:
                return Path(root) / filename

        return None

    @staticmethod
    def filter_sensitive_data(data, data_type="headers"):
        """
        过滤敏感信息，支持headers和json两种类型
        :param data: 原始数据
        :param data_type: 数据类型，headers或json
        :return: 过滤后的数据
        """
        if not isinstance(data, dict):
            return data

        filtered_data = data.copy()

        if data_type == "headers":
            sensitive_keys = ['Authorization', 'authorization', 'Token', 'token']
            for key in sensitive_keys:
                if key in filtered_data:
                    filtered_data[key] = '***FILTERED***'

        elif data_type == "json":
            sensitive_keys = ['password', 'pwd', 'secret', 'token', 'authorization']
            for key in sensitive_keys:
                if key in filtered_data:
                    filtered_data[key] = '***FILTERED***'

        return filtered_data

    @staticmethod
    def format_log_data(data, indent_level=1):
        """
        格式化日志数据，支持字典和字符串
        :param data: 要格式化的数据
        :param indent_level: 缩进级别
        :return: 格式化后的字符串
        """
        indent = "  " * indent_level

        if isinstance(data, dict):
            if not data:
                return "{}"

            lines = []
            for key, value in data.items():
                if isinstance(value, dict):
                    value_str = json.dumps(value, ensure_ascii=False, indent=2)
                    lines.append(f"{indent}{key}: {value_str}")
                else:
                    lines.append(f"{indent}{key}: {value}")
            return "\n".join(lines)

        elif isinstance(data, str):
            # 如果是JSON字符串，尝试格式化
            try:
                json_data = json.loads(data)
                return json.dumps(json_data, ensure_ascii=False, indent=2)
            except:
                return data

        else:
            return str(data)

    @staticmethod
    def validate_case_structure(case_data, required_fields=None):
        """
        验证用例数据结构
        :param case_data: 用例数据
        :param required_fields: 必需字段列表
        :return: 是否有效
        """
        if required_fields is None:
            required_fields = ['feature', 'story', 'title', 'request']

        if not isinstance(case_data, dict):
            INFO.logger.error("用例数据必须是字典格式")
            return False

        for field in required_fields:
            if field not in case_data:
                INFO.logger.error(f"用例缺少必需字段: {field}")
                return False

        return True
