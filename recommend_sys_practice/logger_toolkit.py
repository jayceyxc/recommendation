#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2019-06-24 19:44
# @Author  : yuxuecheng
# @Contact : yuxuecheng@xinluomed.com
# @Site    :
# @File    : logger_toolkit.py
# @Software: PyCharm
# @Description 日志记录工具

import os
import sys
import logging
import time

from logging.handlers import RotatingFileHandler
from logging import Formatter, StreamHandler
from colorlog import ColoredFormatter

from config import base_dir, logs_dir, data_dir


def init_logging(logger, filename):
    """
    初始化日志
    :param logger: 日志记录对象
    :param filename: 日志文件名称
    :return:
    """
    logger.handlers = []
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    filename = os.path.join(logs_dir, filename)
    logger_formatter = '%(asctime)s %(threadName)s %(levelname)-8s ' \
                       '%(filename)s:%(lineno)-4d:%(funcName)-10s: %(message)s'
    colored_formatter = ColoredFormatter(
        fmt=f"%(log_color)s{logger_formatter}",
        datefmt="%Y-%m-%d %H:%M:%S",
        reset=True,
        log_colors={
            'DEBUG':    'cyan',
            'INFO':     'green',
            'WARNING':  'yellow',
            'ERROR':    'red',
            'CRITICAL': 'red,bg_white',
        },
        secondary_log_colors={},
        style='%'
    )

    assert isinstance(logger, logging.Logger)
    logger.setLevel(logging.INFO)
    # FileHandler Info
    file_handler = RotatingFileHandler(
        filename=filename, mode='a', encoding='utf-8')
    file_handler.setFormatter(Formatter(fmt=logger_formatter))
    file_handler.setLevel(logging.INFO)

    logger.addHandler(file_handler)

    # ConsoleHandler Debug
    console_handler = StreamHandler(stream=sys.stdout)
    # console_handler.setFormatter(fmt=logging.Formatter(
    #     '%(name)-12s: %(levelname)-8s %(message)s'))
    console_handler.setFormatter(colored_formatter)
    console_handler.setLevel(logging.DEBUG)

    logger.addHandler(console_handler)

    return logger


def get_logger(file_name_prefix):
    logger = logging.getLogger(file_name_prefix)
    if not logger.handlers:
        logger = init_logging(
            logger=logger, filename=f'{file_name_prefix}_{time.strftime("%Y_%m_%d")}.log')

    return logger


def logger_test():
    logger = get_logger('logger_toolkit')
    logger.debug('debug message')
    logger.info('info message')
    logger.warning('warning message')
    logger.error('error message')
    logger.critical('critical message')


if __name__ == "__main__":
    logger_test()
