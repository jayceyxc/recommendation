#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2020/5/5 20:30
# @Author  : yuxuecheng
# @Contact : jayce123@163.com
# @Site    : 
# @File    : item_cf_movie_recommend.py
# @Software: PyCharm
# @Description: 基于ItemCF算法的电影推荐系统

import random
import math
import os
import json
import codecs

from logger_toolkit import get_logger


class ItemCFRec(object):
    """
    基于ItemCF算法的电影推荐系统
    """
    def __init__(self, datafile, ratio, logger=None):
        self.logger = get_logger('user_cf_recommend')
        if logger is not None:
            self.logger = logger

        # 原始数据路径文件
        self.datafile = datafile
        # 测试集与训练集的比例
        self.ratio = ratio
        self.item_sim_file = 'data/item_sim.json'
        self.data = self.load_data()

        self.train_data, self.test_data = self.split_data(3, 47)
        self.item_sim = self.item_similarity_best()

    # 加载评分数据到data
    def load_data(self):
        self.logger.info('加载数据...')
        data = []
        with codecs.open(self.datafile) as fd:
            for line in fd.readlines():
                userid, itemid, record, _ = line.split('::')
                data.append((userid, itemid, int(record)))

        return data

    def split_data(self, k, seed, M=9):
        """
        拆分数据集为训练集和测试集
        :param k: 参数
        :param seed: 生成随机数的种子
        :param M: 随机数上限
        :return:
        """
        self.logger.info('训练集与测试集切分...')
        train, test = {}, {}
        random.seed(seed)
        for user, item, record in self.data:
            if random.randint(0, M) == k:
                test.setdefault(user, {})
                test[user][item] = record
            else:
                train.setdefault(user, {})
                train[user][item] = record

        return train, test

    def item_similarity_best(self):
        """
        计算item之间的相似度, 惩罚热门物品
        :return:
        """
        self.logger.info('开始计算物品之间的相似度')
        if os.path.exists(self.item_sim_file):
            self.logger.info('物品相似度从文件加载')
            item_sim = json.load(codecs.open(self.item_sim_file, mode='r'))
        else:
            item_sim = dict()
            # 得到每个物品有多少用户产生过行为, 每个物品在多少用户中出现
            item_user_count = dict()
            # 同现矩阵，物品i和物品j共同出现的次数
            count = dict()
            for user, item in self.train_data.items():
                for i in item.keys():
                    item_user_count.setdefault(i, 0)
                    if self.train_data[user][i] > 0.0:
                        item_user_count[i] += 1

                    for j in item.keys():
                        # 设置count中i的默认值为空字典{},设置count中i对应的字典中j对应的默认值为0
                        # In [1]: count = dict()
                        #
                        # In [2]: count.setdefault(1, {}).setdefault(2, 0)
                        # Out[2]: 0
                        #
                        # In [3]: count
                        # Out[3]: {1: {2: 0}}
                        count.setdefault(i, {}).setdefault(j, 0)
                        if self.train_data[user][i] > 0.0 and self.train_data[user][j] > 0.0 and i != j:
                            count[i][j] += 1

            # 同现矩阵 -> 相似度矩阵
            for i, related_items in count.items():
                item_sim.setdefault(i, {})
                for j, cuv in related_items.items():
                    item_sim[i].setdefault(j, 0)
                    # 物品i和j的相似度定义为：物品i和j共同出现的次数除以物品i出现的总次数
                    item_sim[i][j] = cuv / math.sqrt(item_user_count[i] * item_user_count[j])

        self.logger.info(json.dumps(item_sim, indent=2, ensure_ascii=False))
        json.dump(item_sim, codecs.open(self.item_sim_file, mode='w'))

        return item_sim

    def recommend(self, user, k=8, nitems=40):
        """
        为用户进行推荐
        :param user: 用户
        :param k: k个临近物品
        :param nitems: 总共返回n个物品
        :return:
        """
        result = dict()
        u_items = self.train_data.get(user, {})
        for i, pi in u_items.items():
            for j, wj in sorted(self.item_sim[i].items(), key=lambda x: x[1], reverse=True)[0:k]:
                if j in u_items:
                    continue
                result.setdefault(j, 0)
                result[j] += pi * wj

        return dict(sorted(result.items(), key=lambda x: x[1], reverse=True)[0:nitems])

    def precision(self, k=8, nitems=10):
        """
        计算准确率
        :param k:
        :param nitems:
        :return:
        """
        self.logger.info('开始计算准确率...')
        hit = 0
        precision = 0
        for user in self.test_data.keys():
            u_items = self.test_data.get(user, {})
            result = self.recommend(user, k=k, nitems=nitems)
            for item, rate in result.items():
                if item in u_items:
                    hit += 1

            precision += nitems

        return hit / (precision * 1.0)


if __name__ == '__main__':
    logger = get_logger('item_cf_movie_recommend')
    ib = ItemCFRec(datafile='../../data/ml-1m/ratings.dat', ratio=[1, 9], logger=logger)
    logger.info(f'用户1进行推荐的结果如下: {ib.recommend("1")}')
    for k in range(5, 11, 1):
        for nitems in range(10, 22, 2):
            precision = ib.precision(k=k, nitems=nitems)
            logger.info(f'k = {k}, nitems={nitems}, precision is {precision}')
