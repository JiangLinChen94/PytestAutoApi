#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2024/7/20 14:27
# @Author : alin
import os
import yaml.scanner
from configs import setting
from utils.logging_tools.log_control import ERROR


class YamlControl:
    """ 获取 yaml 文件中的数据 """

    def __init__(self, file_dir):
        self.file_dir = str(file_dir)

    def read_yaml_data(self) -> list or dict:
        """
        获取 yaml 中的数据
        :param: fileDir:
        :return: 根据yaml格式返回列表嵌套字典或字典
        """
        # 判断文件是否存在
        try:
            with open(self.file_dir, encoding="utf-8") as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            ERROR.logger.error(f"YAML文件不存在: {self.file_dir}")
            return None
        except yaml.YAMLError as e:
            ERROR.logger.error(f"YAML文件格式错误: {self.file_dir}, 错误: {str(e)}")
            return None
        except Exception as e:
            ERROR.logger.error(f"读取YAML文件异常: {self.file_dir}, 错误: {str(e)}")
            return None

    def __read_yaml_by_key(self, key: str) -> list or dict:
        """
        获取 yaml 中某一个键的值
        :param: fileDir:
        :param: key: 读取的键
        :return: 根据yaml格式返回列表嵌套字典或字典
        """
        # 判断文件是否存在
        res = YamlControl(self.file_dir).read_yaml_data()
        return res[key]

    def write_yaml_data(self, data: dict):
        """
        写入YAML文件，统一错误处理
        :param data: 要写入的数据
        :return: 是否成功
        """
        try:
            with open(self.file_dir, "a", encoding="utf-8") as f:
                yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)
            return True
        except Exception as e:
            ERROR.logger.error(f"写入YAML文件失败: {self.file_dir}, 错误: {str(e)}")
            return False

    def clear_yaml_data(self):
        """
        yaml 文件清空
        :return: None
        """
        with open(self.file_dir, 'w', encoding='utf-8') as file:
            pass

    def update_yaml_data(self, key: str, value) -> bool:
        """
        eg: extract_yaml_control.write_yaml_data({"name": "value"})
        更改 yaml 文件中的值, 并且保留注释内容
        备注：如果字典中存在的键有相同，则会全部修改
        :param key: 字典的key
        :param value: 写入的值
        :return:
        """
        with open(self.file_dir, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        flag = False
        with open(self.file_dir, 'w', encoding='utf-8') as file:
            for line in lines:
                left_str = line.split(":")[0]
                if key == left_str.strip() and '#' not in line:
                    line = f"{left_str}: {value}\n"
                    flag = True
                file.write(line)
        return flag

    @staticmethod
    def read_extract(file_path=setting.extract_file_name):
        """
        读取 extract.yaml 文件中的数据
        :param file_path: 文件路径，默认PytestAutoApi\extract.yaml路径
        :return: 根据yaml格式返回列表嵌套字典或字典
        """
        try:
            # 获取PytestAutoApi路径
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            extract_path = os.path.join(base_dir, file_path)
            return YamlControl(extract_path).read_yaml_data()
        except Exception as e:
            print(f"读取 extract.yaml 文件失败: {str(e)}")
            return {}

    @staticmethod
    def read_extract_by_key(key, file_path=setting.extract_file_name):
        """
        读取 extract.yaml 文件中的数据
        :param key: 需要读取的键
        :param file_path: 文件路径，默认PytestAutoApi\extract.yaml路径
        :return: 根据yaml格式返回列表嵌套字典或字典
        """
        try:
            # 获取PytestAutoApi路径
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            extract_path = os.path.join(base_dir, file_path)
            print(extract_path)
            return YamlControl(extract_path).__read_yaml_by_key(key)
        except Exception as e:
            print(f"读取 extract.yaml 文件失败: {str(e)}")
            return None

    @staticmethod
    def write_extract(data: dict, file_path=setting.extract_file_name):
        """
        向 extract.yaml 文件中写入数据
        :param file_path: 文件路径，默认PytestAutoApi\extract.yaml路径
        :param data: 传入字典格式路径
        :return:
        """
        try:
            # 获取PytestAutoApi路径
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            extract_path = os.path.join(base_dir, file_path)
            YamlControl(extract_path).write_yaml_data(data)
        except Exception as e:
            print(f"写入 extract.yaml 文件失败: {str(e)}")
            return None

    @staticmethod
    def clear_extract(file_path=setting.extract_file_name):
        """
        清空 extract.yaml 文件中数据
        :param file_path: 文件路径，默认PytestAutoApi\extract.yaml路径
        :return:
        """
        try:
            # 获取PytestAutoApi路径
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            extract_path = os.path.join(base_dir, file_path)
            YamlControl(extract_path).clear_yaml_data()
        except Exception as e:
            print(f"清空 extract.yaml 文件失败: {str(e)}")
            return None


if __name__ == '__main__':
    # YamlControl.write_extract({"token": "1231231231"})
    # YamlControl.clear_extract()
    result = YamlControl.read_extract_by_key("token")
    print(result)  # extract_yaml_path = "D:\Script\PytestAutoApi\extract.yaml"
    # extract_yaml_control = YamlControl(extract_yaml_path)
    # print(extract_yaml_control.read_yaml_data())
    # extract_yaml_control.write_yaml_data({"name": "value"})
    # extract_yaml_control.update_yaml_data("name", "update_value")
    # print(extract_yaml_control.read_yaml_data())
