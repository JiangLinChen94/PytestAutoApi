#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2026/3/26 14:40
# @Author : alin
import pymysql
from utils.logging_tools.log_control import INFO, ERROR
from utils.file_tools.config_control import config


class MysqlControl:
    """MySQL 数据库操作类（生产级优化）"""

    def __init__(self):
        # 数据库配置（建议放到配置文件，这里先写死）
        self.db_conf = {
            "user": config.get("mysql", "db_user"),
            "password": config.get("mysql", "db_password"),
            "host": config.get("mysql", "db_host"),
            "database": config.get("mysql", "db_database"),
            "port": config.get("mysql", "db_port"),
            "charset": "utf8mb4",
            "cursorclass": pymysql.cursors.DictCursor  # 返回字典格式，更易用
        }

    def create_connection(self):
        """创建数据库连接（带异常捕获）"""
        try:
            conn = pymysql.connect(**self.db_conf)
            INFO.logger.info("MySQL 连接成功")
            return conn
        except Exception as e:
            ERROR.logger.error(f"MySQL 连接失败：{str(e)}")
            raise

    def execute_sql(self, sql, args=None):
        """
        执行SQL（支持查询/增删改）
        :param sql: SQL语句
        :param args: 参数化查询，防SQL注入
        :return: 查询返回第一条，增删改自动提交
        """
        conn = None
        cs = None
        try:
            conn = self.create_connection()
            cs = conn.cursor()

            # 执行SQL
            INFO.logger.info(f"执行SQL：{sql}")
            rows = cs.execute(sql, args)

            # 查询语句 → 返回结果
            if sql.strip().upper().startswith("SELECT"):
                result = cs.fetchone()  # 单条
                # result = cs.fetchall() # 多条
                INFO.logger.info(f"查询结果：{result}")
                return result

            # 增删改 → 提交事务
            else:
                conn.commit()
                INFO.logger.info(f"执行成功，受影响行数：{rows}")
                return rows

        except Exception as e:
            if conn:
                conn.rollback()  # 失败回滚
            ERROR.logger.error(f"SQL执行失败：{str(e)}")
            raise

        finally:
            # 无论如何都关闭资源，防止连接泄漏
            if cs:
                cs.close()
            if conn:
                conn.close()
                INFO.logger.info("MySQL 连接已关闭")


if __name__ == '__main__':
    mysql_obj = MysqlControl()
    sql_value = mysql_obj.execute_sql(
        "select * from t_record_store_transfer where owner_biz_no = 'LSHM20312711624236728326272'")
