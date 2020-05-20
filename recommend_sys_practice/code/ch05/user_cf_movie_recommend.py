#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2020/5/4 13:02
# @Author  : yuxuecheng
# @Contact : jayce123@163.com
# @Site    : 
# @File    : user_cf_movie_recommend
# @Software: PyCharm
# @Description: 基于UserCF算法的电影推荐系统

import random
import math
import json
import os
import codecs

from logger_toolkit import get_logger


class UserCFRec(object):
    """
    基于UserCF算法的电影推荐系统
    """
    def __init__(self, datafile, logger=None):
        self.logger = get_logger('user_cf_recommend')
        if logger is not None:
            self.logger = logger
        self.datafile = datafile
        self.data = self.load_data()

        self.train_data, self.test_data = self.split_data(3, 47)
        self.user_sim = self.user_similarity_best()

    # 加载评分数据到data
    def load_data(self):
        self.logger.info('加载数据...')
        data = []
        with codecs.open(self.datafile) as fd:
            for line in fd.readlines():
                userid, itemid, record, _ = line.split('::')
                data.append((userid, itemid, int(record)))

        return data

    def split_data(self, k, seed, M=8):
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

    def user_similarity_best(self):
        """
        计算用户之间的相似度，采用惩罚热门商品和优化算法复杂度的算法
        :return:
        """
        self.logger.info('开始计算用户之间的相似度...')
        if os.path.exists('data/user_sim.json'):
            self.logger.info('用户相似度从文件加载...')
            user_sim = json.load(codecs.open('data/user_sim.json', mode='r', encoding='utf8'))
            self.logger.info('用户相似度加载完成')
        else:
            # 得到每一个item被哪些user评价过
            item_users = dict()
            for u, items in self.train_data.items():
                for i in items.keys():
                    item_users.setdefault(i, set())
                    if self.train_data[u][i] > 0:
                        item_users[i].add(u)

            # 构建倒排表
            # 用户之间的兴趣相似度
            count = dict()
            # 用户评价商品的个数
            user_item_count = dict()
            for i, users in item_users.items():
                for u in users:
                    user_item_count.setdefault(u, 0)
                    user_item_count[u] += 1
                    count.setdefault(u, {})
                    for v in users:
                        count[u].setdefault(v, 0)
                        if u == v:
                            continue
                        count[u][v] += 1 / math.log(1 + len(users))

            # 构建相似度矩阵
            user_sim = dict()
            for u, related_users in count.items():
                user_sim.setdefault(u, {})
                # v 是相关用户的用户ID，cuv是用户u和用户v的共同评价商品的相似度
                for v, cuv in related_users.items():
                    if u == v:
                        continue
                    user_sim[u].setdefault(v, 0.0)
                    # user_sim[u][v]是用户u和用户v的兴趣相似度
                    user_sim[u][v] = cuv / math.sqrt(user_item_count[u] * user_item_count[v])

            json.dump(user_sim, codecs.open('data/user_sim.json', mode='w'))
            self.logger.info('用户相似度计算完成')

        return user_sim

    def recommend(self, user, k=8, nitems=40):
        """
        为用户user进行物品推荐
        :param user: 用户user
        :param k: 选取k个近邻用户
        :param nitems: 取nitems个物品
        :return:
        """
        result = dict()
        # have_score_items是用户user评价过的商品
        have_score_items = self.train_data.get(user, {})
        # v是用户user的相似用户，wuv是用户user和用户v的兴趣相似度
        for v, wuv in sorted(self.user_sim[user].items(), key=lambda x: x[1], reverse=True)[0:k]:
            # i是用户v评价过的商品ID，rvi是用户v对商品i的评价
            for i, rvi in self.train_data[v].items():
                if i in have_score_items:
                    continue

                result.setdefault(i, 0)
                result[i] += wuv * rvi

        return dict(sorted(result.items(), key=lambda x: x[1], reverse=True)[0:nitems])

    def precision(self, k=8, nitems=10):
        """
        计算准确率
        :param k: 近邻用户数
        :param nitems: 推荐的item个数
        :return:
        """
        self.logger.info('开始计算准确率...')
        hit = 0
        precision = 0
        for user in self.train_data.keys():
            # tu: 用户实际评分的电影ID
            tu = self.test_data.get(user, {})
            # rank: 推荐系统推荐的电影ID
            rank = self.recommend(user, k=k, nitems=nitems)
            for item, rate in rank.items():
                if item in tu:
                    hit += 1

            precision += nitems

        self.logger.info(f'hit: {hit}')
        self.logger.info(f'precision: {precision}')
        return hit / (precision * 1.0)


if __name__ == '__main__':
    logger = get_logger('user_cf_recommend')
    cf = UserCFRec('../../data/ml-1m/ratings.dat', logger=logger)
    result = cf.recommend('1')
    logger.info(f'user "1" recommend result is {result}')
    precision = cf.precision()
    logger.info(f'k=8, n=10, precision is {precision}')
    for k in range(5, 10, 1):
        for nitems in range(10, 20, 2):
            precision = cf.precision(k=k, nitems=nitems)
            logger.info(f'k = {k}, nitems={nitems}, precision is {precision}')


