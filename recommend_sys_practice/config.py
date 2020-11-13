#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2019-05-28 21:00
# @Author  : yuxuecheng
# @Contact : yuxuecheng@xinluomed.com
# @Site    :
# @File    : server_conf.py
# @Software: PyCharm
# @Description

import os


def make_dirs_not_exists(dir_path):
    """
    如果目录不存在则创建目录
    """
    if not os.path.exists(dir_path):
        print(f'创建目录: {dir_path}')
        os.makedirs(dir_path)
    else:
        print(f'目录已存在: {dir_path}')


base_dir = os.path.dirname(os.path.abspath(__file__))
print(base_dir)
logs_dir = os.path.join(base_dir, 'logs')
data_dir = os.path.join(base_dir, 'data')
make_dirs_not_exists(logs_dir)
make_dirs_not_exists(data_dir)
