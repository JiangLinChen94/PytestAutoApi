#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2026/3/25 19:05
# @Author : alin
import sys
import os
import pytest
import allure
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.other_tools.model_control import verify_yaml
from utils.case_tools.case_control import use_case_execution
from utils.case_tools.ddt_control import read_testcase
from utils.case_tools.business_flow_control import BusinessFlowControl


class TestAllCase:
    pass


def create_testcase(yaml_path):
    """
    创建测试用例函数
    支持三种用例类型：
    1. 业务流程用例（跨文件组合）
    2. 流程用例（单文件多接口）
    3. 单接口用例（普通/数据驱动）
    """
    
    # 判断用例类型
    if BusinessFlowControl.is_business_flow(yaml_path):
        # 业务流程用例
        case_list = BusinessFlowControl.read_business_flow(yaml_path)
    else:
        # 普通用例（流程用例/单接口用例）
        case_list = read_testcase(yaml_path)
    
    @pytest.mark.parametrize("case_info", case_list)
    def func(self, case_info):
        global new_case_info
        
        # 流程用例处理（包括业务流程用例）
        if isinstance(case_info, list):
            # 流程用例：多个接口按顺序执行
            allure.dynamic.feature("流程测试用例")
            allure.dynamic.story("多接口流程测试")
            
            for i, ci in enumerate(case_info):
                # 校验YAML
                new_case_info = verify_yaml(ci)
                
                # 设置Allure报告标题
                allure.dynamic.title(f"流程步骤 {i+1}: {new_case_info.title}")
                
                # 执行测试用例（包含变量替换和提取功能）
                use_case_execution(new_case_info)
                
                # 添加步骤分隔
                if i < len(case_info) - 1:
                    allure.dynamic.description(f"步骤 {i+1} 完成，准备执行步骤 {i+2}")
        else:
            # 单接口{}，数据驱动{},{},{}
            # 校验YAML
            new_case_info = verify_yaml(case_info)
            
            # 定制Allure报告
            allure.dynamic.feature(new_case_info.feature)
            allure.dynamic.story(new_case_info.story)
            allure.dynamic.title(new_case_info.title)
            
            # 用例的标准化处理
            use_case_execution(new_case_info, str(yaml_path))

    return func


# 获取当前文件的路径
current_path = Path(__file__).parent
# 循环获取到所有的yaml文件
yaml_file_list = list(current_path.glob("**/*.yaml"))
for yaml_path in yaml_file_list:
    # 将用例反射给TestAllCase类
    setattr(TestAllCase, "test_" + yaml_path.stem, create_testcase(yaml_path))