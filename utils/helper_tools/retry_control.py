#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2026/4/1 14:19
# @Author : alin
import time
from utils.helper_tools.log_control import logger


class RetryControl:
    """
    重跑控制类，用于实现用例失败重跑功能
    """

    @staticmethod
    def execute_with_retry(case_execution_func, case_info, retry_count: int):
        """
        带重跑功能的用例执行
        :param case_execution_func: 用例执行函数
        :param case_info: 用例信息
        :param retry_count: 重跑次数
        :return: 执行结果
        """
        if retry_count is None or retry_count <= 0:
            # 无重跑配置，直接执行
            return case_execution_func(case_info)

        max_attempts = retry_count + 1  # 总尝试次数 = 重跑次数 + 初始执行
        
        for attempt in range(1, max_attempts + 1):
            try:
                logger.info(f"🔄 第 {attempt} 次执行用例: {case_info.title}")
                
                result = case_execution_func(case_info)
                
                if attempt > 1:
                    logger.info(f"✅ 重跑成功！第 {attempt} 次执行通过")
                
                return result
                
            except Exception as e:
                if attempt < max_attempts:
                    # 计算下次重跑间隔（指数退避策略）
                    wait_time = 2 ** (attempt - 1)  # 1, 2, 4, 8...秒
                    logger.warning(f"⚠️ 第 {attempt} 次执行失败，{wait_time} 秒后重跑...")
                    logger.warning(f"   失败原因: {str(e)}")
                    
                    # 显示重跑倒计时
                    for remaining in range(wait_time, 0, -1):
                        logger.info(f"⏳ 重跑倒计时: {remaining} 秒")
                        time.sleep(1)
                    
                    logger.info(f"🚀 开始第 {attempt + 1} 次重跑")
                else:
                    # 最后一次尝试也失败
                    logger.error(f"❌ 用例执行失败，已达到最大重跑次数 {retry_count}")
                    logger.error(f"   最终失败原因: {str(e)}")
                    raise

    @staticmethod
    def should_retry(exception) -> bool:
        """
        判断是否应该重跑（可扩展的异常过滤逻辑）
        :param exception: 异常对象
        :return: 是否应该重跑
        """
        # 默认所有异常都重跑，可以根据需要添加过滤逻辑
        return True

    @staticmethod
    def get_retry_delay(attempt: int) -> int:
        """
        获取重跑延迟时间（指数退避策略）
        :param attempt: 当前尝试次数
        :return: 延迟秒数
        """
        return min(2 ** (attempt - 1), 60)  # 最大延迟60秒