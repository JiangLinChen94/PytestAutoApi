#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2026/4/1 11:07
# @Author : alin
import os
import yaml
from configs import setting


class ConfigControl:
    _instance = None
    _env = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.load_config()
        return cls._instance

    def load_config(self):
        # 自动获取项目根目录 → 绝对路径（永不报错）
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self._env = os.getenv("ENV", setting.ENV)

        # 拼接正确路径
        config_path = os.path.join(base_dir, "configs", f"{self._env}.yaml")

        # 加载配置
        with open(config_path, encoding="utf-8") as f:
            self.config = yaml.safe_load(f)

    def get(self, key, sub_key=None):
        if sub_key:
            return self.config[key][sub_key]
        return self.config[key]


# 全局配置对象
config = ConfigControl()
