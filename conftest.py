#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2026/3/25 17:25
# @Author : alin
import pytest
from utils.file_tools.yaml_control import YamlControl


@pytest.fixture(scope="session", autouse=True)
def auto_clear():
    YamlControl.clear_extract()
