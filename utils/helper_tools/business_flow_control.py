#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2026/4/1 16:05
# @Author : alin
import os
import yaml
from pathlib import Path
from utils.helper_tools.log_control import logger
from utils.helper_tools.ddt_control import read_testcase
from utils.helper_tools.common_utils import CommonUtils


class BusinessFlowControl:
    """业务流程用例控制器"""

    @staticmethod
    def read_business_flow(yaml_path):
        """
        读取业务流程用例文件
        :param yaml_path: 业务流程用例文件路径
        :return: 流程用例列表 [[{},{},...]]
        """
        try:
            # 使用通用工具类读取YAML文件
            flow_config = CommonUtils.read_yaml_file(yaml_path)

            if not flow_config:
                logger.error(f"业务流程用例文件为空: {yaml_path}")
                return []

            # 验证业务流程用例格式
            if not BusinessFlowControl._validate_flow_format(flow_config):
                logger.error(f"业务流程用例格式错误: {yaml_path}")
                return []

            scene_name = flow_config.get("scene_name", "")
            desc = flow_config.get("desc", "")
            cases = flow_config.get("cases", [])
            config = flow_config.get("config", {})

            logger.info(f"📋 开始加载业务流程: {scene_name}")
            logger.info(f"📝 流程描述: {desc}")

            # 构建流程用例列表
            flow_cases = BusinessFlowControl._build_flow_cases(yaml_path, cases)

            if flow_cases:
                logger.info(f"🎯 业务流程加载完成，共 {len(flow_cases)} 个步骤")
                return [flow_cases]  # 包装成流程用例格式
            else:
                logger.error(f"❌ 业务流程用例加载失败: {yaml_path}")
                return []

        except FileNotFoundError:
            logger.error(f"业务流程用例文件不存在: {yaml_path}")
            return []
        except yaml.YAMLError as e:
            logger.error(f"业务流程用例文件格式错误: {yaml_path}, 错误: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"读取业务流程用例异常: {yaml_path}, 错误: {str(e)}")
            return []

    @staticmethod
    def is_business_flow(yaml_path):
        """
        判断是否为业务流程用例文件
        :param yaml_path: 文件路径
        :return: True/False
        """
        try:
            content = CommonUtils.read_yaml_file(yaml_path)

            if isinstance(content, dict):
                return "scene_name" in content and "cases" in content
            return False

        except:
            return False

    @staticmethod
    def _validate_flow_format(flow_config):
        """
        验证业务流程用例格式
        :param flow_config: 流程配置
        :return: 是否有效
        """
        if not isinstance(flow_config, dict):
            return False

        if "scene_name" not in flow_config or "cases" not in flow_config:
            return False

        if not isinstance(flow_config.get("cases"), list):
            return False

        return True

    @staticmethod
    def _build_flow_cases(yaml_path, cases):
        """
        构建流程用例列表
        :param yaml_path: 业务流程文件路径
        :param cases: 用例配置列表
        :return: 流程用例列表
        """
        flow_cases = []

        for i, case_config in enumerate(cases):
            case_file = case_config.get("case")
            case_desc = case_config.get("desc", "")

            if not case_file:
                logger.error(f"第 {i + 1} 个用例配置缺少case字段")
                continue

            # 构建用例文件完整路径（支持子目录查找）
            case_dir = Path(yaml_path).parent
            case_path = CommonUtils.find_file_in_directory(case_dir, case_file)

            if not case_path or not case_path.exists():
                logger.error(f"用例文件不存在: {case_file}，在目录 {case_dir} 及其子目录中未找到")
                continue

            # 读取单个用例文件
            case_list = read_testcase(str(case_path))

            if case_list:
                # 如果是流程用例，直接添加
                if isinstance(case_list[0], list):
                    flow_cases.extend(case_list[0])
                else:
                    # 单接口用例，包装成列表
                    flow_cases.append(case_list[0])

                logger.info(f"✅ 加载第 {i + 1} 步: {case_desc} ({case_file})")
                logger.info(f"   文件路径: {case_path}")
            else:
                logger.error(f"❌ 加载第 {i + 1} 步失败: {case_file}")

        return flow_cases
