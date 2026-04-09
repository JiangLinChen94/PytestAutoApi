#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2026/3/26 14:40
# @Author : alin
import re
import yaml
from dataclasses import asdict
from string import Template
from utils.helper_tools.helper_control import HelperControl
from utils.file_tools.yaml_control import YamlControl


class ReplaceControl:
    @staticmethod
    def function_replace(yaml_str: str):
        # 在yaml中调用python方法的格式：${方法名(参数)}
        regexp = r"\$\{(\w+)\((.*?)\)\}"
        # 通过正则匹配yaml中的表达式
        func_list = re.findall(regexp, yaml_str)
        # 循环：下标为0的是方法名，下标为1的是参数
        for func in func_list:
            if func[1] == "":  # 没有参数
                # 通过一个方法名字符串，如何去调用DebugTalk中的abc方法
                new_value = getattr(HelperControl, func[0])()
            else:  # 有参数，区分1个参数和多个参数
                new_value = getattr(HelperControl, func[0])(*func[1].split(","))

            # 拼接旧的值
            old_value = "${" + func[0] + "(" + func[1] + ")}"
            # 替换时确保路径字符串正确处理
            if isinstance(new_value, str) and "\\" in new_value:
                # 对于包含反斜杠的路径，使用原始字符串表示
                new_value = new_value.replace("\\", "/")  # 将反斜杠转换为正斜杠
            # 替换
            yaml_str = yaml_str.replace(old_value, str(new_value))
        return yaml_str

    @staticmethod
    def variable_replace(yaml_str: str):
        """
        替换 yaml 中的 ${token} 格式变量
        例如：$token → 真实token值
        """
        # 读取全局变量文件 extract.yaml
        extract_data = YamlControl.read_extract()

        # 正则匹配：$变量名（如 $token, $orderId, $userId）
        regexp = r"\$\{(\w+)\}"
        var_list = re.findall(regexp, yaml_str)

        # 循环替换所有 $变量
        for var_name in var_list:
            # 从全局变量中取值
            real_value = extract_data.get(var_name, f"$${var_name}_NOT_FOUND")

            yaml_str = yaml_str.replace(f"${{{var_name}}}", str(real_value))
        return yaml_str

    def replace_all(self, data):
        if isinstance(data, str):
            # 输入是字符串
            yaml_str = data
        else:
            # 输入是对象 CaseInfo → 转字符串
            yaml_str = yaml.safe_dump(asdict(data), sort_keys=False, allow_unicode=True)

        # 执行替换
        yaml_str = self.function_replace(yaml_str)
        yaml_str = self.variable_replace(yaml_str)

        # 如果传入的是对象 → 转回对象
        if not isinstance(data, str):
            new_dict = yaml.safe_load(yaml_str)
            return data.__class__(**new_dict)

        # 传入的是字符串 → 直接返回字符串
        return yaml_str


if __name__ == '__main__':
    yaml_str = """{"Authorization": "Bearer ${token}", "cookie": "Bearer ${read_extract(token)}"}"""
    new_yaml_str = ReplaceControl().replace_all(yaml_str)

    print(new_yaml_str)