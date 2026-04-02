#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2026/3/25 18:43
# @Author : alin
import requests
from utils.helper_tools.log_control import logger
from configs import setting


class RequestsControl:
    sess = requests.session()

    def send_all_request(self, **kwargs):
        """
        发送用例请求
        :param kwargs: 用例传值，如url，method等参数
        :return:
        """
        # 公共参数
        header = setting.global_header

        # 处理请求参数
        for key, value in kwargs.items():
            if key == "header":
                kwargs["header"].update(header)
            if key == "files":
                for file_key, file_value in value.items():
                    value[file_key] = open(file_value, "rb")

        try:
            # 发送请求
            response = RequestsControl.sess.request(**kwargs)

            # 检查响应状态码，判断是否失败
            if response.status_code >= 400:
                # 接口失败时记录详细的请求和响应信息
                self._log_failed_request(kwargs, response)

            return response

        except requests.exceptions.RequestException as e:
            # 请求异常时记录详细的错误信息
            logger.error(f"请求发送失败: {str(e)}")
            self._log_failed_request(kwargs, None, str(e))
            raise
        except Exception as e:
            # 其他异常
            logger.error(f"请求处理过程中发生未知错误: {str(e)}")
            self._log_failed_request(kwargs, None, str(e))
            raise

    def _log_failed_request(self, request_kwargs, response=None, error_msg=None):
        """
        记录失败的请求详细信息
        :param request_kwargs: 请求参数
        :param response: 响应对象
        :param error_msg: 错误信息
        """
        logger.error("接口请求失败，详细信息如下：")

        # 记录请求信息
        logger.error("请求信息：")
        for key, value in request_kwargs.items():
            # 敏感信息处理（如密码、token等）
            if key in ['json', 'data'] and isinstance(value, dict):
                # 创建敏感信息过滤后的副本
                filtered_value = self._filter_sensitive_info(value)
                logger.error(f"   {key}: {filtered_value}")
            elif key == 'headers' and isinstance(value, dict):
                # 过滤敏感头信息
                filtered_headers = self._filter_sensitive_headers(value)
                logger.error(f"   {key}: {filtered_headers}")
            else:
                logger.error(f"   {key}: {value}")

        # 记录响应信息（如果有）
        if response is not None:
            logger.error("响应信息：")
            logger.error(f"状态码: {response.status_code}")
            logger.error(f"响应头: {dict(response.headers)}")
            logger.error(f"响应内容: {response.text}")

        # 记录错误信息（如果有）
        if error_msg:
            logger.error(f"错误信息: {error_msg}")

    def _filter_sensitive_info(self, data):
        """
        过滤敏感信息
        :param data: 原始数据
        :return: 过滤后的数据
        """
        sensitive_keys = ['password', 'token', 'authorization', 'secret', 'key', 'pwd']
        filtered_data = data.copy()

        for key in sensitive_keys:
            if key in filtered_data:
                filtered_data[key] = '***FILTERED***'

        return filtered_data

    def _filter_sensitive_headers(self, headers):
        """
        过滤敏感头信息
        :param headers: 原始头信息
        :return: 过滤后的头信息
        """
        sensitive_headers = ['Authorization', 'authorization', 'Token', 'token']
        filtered_headers = headers.copy()

        for header in sensitive_headers:
            if header in filtered_headers:
                filtered_headers[header] = '***FILTERED***'

        return filtered_headers
