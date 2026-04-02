#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2026/3/25 14:07
# @Author : alin
import os
import pytest
import time


if __name__ == '__main__':
    pytest.main()
    time.sleep(3)
    os.system("allure generate ./report/temp -o ./report/html --clean")
