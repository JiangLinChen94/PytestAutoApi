#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2026/3/25 20:34
# @Author : alin
import copy
import re
from dataclasses import asdict
import jsonpath
import yaml
from utils.helper_tools.model_control import CaseInfo
from utils.file_tools.yaml_control import YamlControl
from utils.helper_tools.replace_control import ReplaceControl


class ExtractControl:
    # res=body=响应体
    # print(res.text)  # 返回字符串类型的数据
    # print(res.content)  # 返回二进制数据
    # print(res.json())  #返回字典格式数据
    # print(res.headers)  # 返回响应头
    # print(res.cookies)  # 返回响应cookie
    # print(res.status_code)  # 响应码
    # print(res.reason)  # 返回响应信息
    # print(res.encoding)  # 返回编码格式
    # print(res.elapsed)  # 耗时
    @staticmethod
    def extract(var_name, resp, attr, expr: str, index: int):
        """
        截取参数写入extract.yaml文件
        :param var_name: 要保存的变量名，比如 token
        :param resp: 接口响应对象（requests返回的response）
        :param attr: 从响应的哪里取？比如 json / text
        :param expr: 提取表达式：jsonpath 或 正则
        :param index: 取第几个结果（下标）
        :return:
        """
        # 1.获取response的值。深拷贝一份resp，
        # 深拷贝不会改变原来的值，浅拷贝会改变原因的值。
        response = copy.deepcopy(resp)
        # 2.把json()方法变成一个属性
        try:
            response.json = response.json()
        except Exception:
            response.json = {"msg": "response is not json data"}
        # 3.通过res对象和属性字符串如何获取属性的值
        data = getattr(response, attr)
        # 4.判断提取的方式是正则还是jsonpath
        if expr.startswith("$"):
            extract_list = jsonpath.jsonpath(dict(data), expr)
        else:
            extract_list = re.findall(expr, data)
        # 5.通过下标取值
        if extract_list:
            var_value = extract_list[index]
        else:
            var_value = "not extract data"
        # 6.把数据写入到extract.yaml里面
        YamlControl.write_extract({var_name: var_value})

    # 读取extract.yaml里面的数据并使用(请求之前)
    @staticmethod
    def change_extract(case_info: CaseInfo):
        # 1.把case_info转化为字符串
        case_str = yaml.safe_dump(asdict(case_info))
        # 2.替换
        new_case_str = ReplaceControl().replace_all(case_str)
        # 3.把字符串转化为CaseInfo对象并返回
        new_obj = CaseInfo(**yaml.safe_load(new_case_str))
        return new_obj

    @staticmethod
    def change(case_info: CaseInfo):
        # 1.case_info
        yaml_str = yaml.safe_dump(case_info)
        # 2.替换
        # new_str=Template(case_str).safe_substitute(read_extract())
        yaml_str = ReplaceControl().replace_all(yaml_str)
        # 3.把字符串转化为CaseInfo对象并返回
        dict_data = yaml.safe_load(yaml_str)
        return dict_data
