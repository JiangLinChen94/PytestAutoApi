#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2026/3/26 14:40
# @Author : alin
import yaml
from datetime import date, datetime
from utils.logging_tools.log_control import ERROR


def read_testcase(yaml_path):
    """
    读取测试用例，自动识别三种用例类型：
    1. 流程用例（多个接口）：返回 [[{},{},...]]
    2. 数据驱动用例（带 parametrize）：返回 [{},{},...]
    3. 普通单接口用例：返回 [{}]
    """
    try:
        with open(yaml_path, encoding="utf-8") as f:
            case_list = yaml.safe_load(f) or []

        # 空文件保护
        if not isinstance(case_list, list):
            case_list = [case_list]

        # 流程用例：文件里有多个接口
        if len(case_list) >= 2:
            return [case_list]

        # 单接口场景
        if case_list:
            case_info = case_list[0]
            if isinstance(case_info, dict) and "parametrize" in case_info:
                # 检查parametrize是否为有效的数据驱动配置
                parametrize_value = case_info.get("parametrize")

                if parametrize_value is not None and parametrize_value != "null":
                    # 数据驱动用例
                    result = ddts(case_info)
                    if result:  # 只有当ddts返回有效结果时才使用
                        return result
                    else:
                        ERROR.logger.error("数据驱动用例生成失败，使用普通单接口用例")

        # 普通单接口用例
        return case_list

    except FileNotFoundError:
        ERROR.logger.error(f"测试用例文件不存在: {yaml_path}")
        return []
    except yaml.YAMLError as e:
        ERROR.logger.error(f"YAML文件解析错误: {str(e)}")
        return []
    except Exception as e:
        ERROR.logger.error(f"读取测试用例时发生未知错误: {str(e)}")
        return []


def ddts(case_info: dict):
    """
    解析数据驱动 parametrize，生成多条用例
    支持格式：
    parametrize:
      - [key1, key2]
      - [v1, v2]
      - [v3, v4]
    替换 $ddt{key1}、$ddt{key2}
    """
    try:
        data_list = case_info.get("parametrize", [])

        # 检查parametrize是否为有效列表
        if not isinstance(data_list, list) or len(data_list) < 2:
            ERROR.logger.error("parametrize配置无效：必须是列表且至少包含2行（参数名+数据）")
            return []

        # 检查每行列数是否一致
        args = data_list[0]
        if not isinstance(args, list):
            ERROR.logger.error("参数名行必须是列表格式")
            return []

        arg_len = len(args)

        for i, row in enumerate(data_list[1:], 1):
            if not isinstance(row, list):
                ERROR.logger.error(f"第{i + 1}行数据格式错误：必须是列表")
                return []
            if len(row) != arg_len:
                ERROR.logger.error(f"第{i + 1}行数据数量({len(row)})与参数名数量({arg_len})不匹配")
                return []

        # 转字符串方便批量替换
        case_str = yaml.dump(case_info, allow_unicode=True)
        new_list = []

        # 遍历每一行数据
        for i, row in enumerate(data_list[1:], 1):
            tmp_str = case_str

            for key, value in zip(args, row):
                # 安全替换，确保日期等类型保持为字符串
                if value is None:
                    replace_val = "null"
                elif isinstance(value, bool):
                    replace_val = str(value).lower()
                elif isinstance(value, (date, datetime)):
                    # 日期类型转换为字符串格式
                    replace_val = value.strftime("%Y-%m-%d")
                else:
                    replace_val = str(value)

                # 替换占位符
                old_pattern = f"$ddt{{{key}}}"
                tmp_str = tmp_str.replace(old_pattern, replace_val)

            # 转回字典，使用自定义的yaml加载器避免日期转换
            try:
                new_case = yaml.safe_load(tmp_str)
                new_case.pop("parametrize", None)

                # 在数据驱动阶段就进行变量替换
                new_case = _replace_variables_in_case(new_case)
                
                # 确保所有日期字段都是字符串格式
                new_case = _ensure_string_dates(new_case)
                new_list.append(new_case)

            except yaml.YAMLError as e:
                ERROR.logger.error(f"第{i}组数据YAML解析失败: {str(e)}")
                continue
            except Exception as e:
                ERROR.logger.error(f"第{i}组数据处理失败: {str(e)}")
                continue

        return new_list

    except Exception as e:
        ERROR.logger.error(f"数据驱动处理过程中发生未知错误: {str(e)}")
        return []


def _replace_variables_in_case(case_data):
    """
    在数据驱动阶段替换用例中的变量和函数调用
    """
    from utils.case_tools.replace_control import ReplaceControl
    
    # 将用例数据转换为字符串进行替换
    case_str = yaml.dump(case_data, allow_unicode=True)
    
    # 执行变量替换（先替换变量）
    case_str = ReplaceControl().variable_replace(case_str)
    
    # 执行函数替换（再执行函数调用）
    case_str = ReplaceControl().function_replace(case_str)
    
    # 转换回字典
    return yaml.safe_load(case_str)


def _ensure_string_dates(data):
    """
    确保所有日期字段都是字符串格式
    """
    if isinstance(data, dict):
        return {k: _ensure_string_dates(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [_ensure_string_dates(item) for item in data]
    elif isinstance(data, (date, datetime)):
        return data.strftime("%Y-%m-%d")
    else:
        return data


if __name__ == '__main__':
    # 测试代码
    test_case = {
        "feature": "测试",
        "request": {
            "json": {"param1": "$ddt{key1}", "param2": "$ddt{key2}"}
        },
        "parametrize": [
            ["key1", "key2"],
            ["value1", "value2"],
            ["value3", "value4"]
        ]
    }

    result = ddts(test_case)
    print("测试结果:", result)