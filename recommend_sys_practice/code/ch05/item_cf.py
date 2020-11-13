#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2020/5/5 20:00
# @Author  : yuxuecheng
# @Contact : jayce123@163.com
# @Site    : 
# @File    : item_cf.py
# @Software: PyCharm
# @Description: ItemCF算法原理——计算物品相似度和用户对未知物品的可能评分

import math
import json

from logger_toolkit import get_logger


class ItemCF(object):
    """
    基于物品的协同过滤算法
    """
    def __init__(self, logger=None):
        super().__init__()
        self.logger = get_logger('item_cf')
        if logger is not None:
            self.logger = logger
        self.user_score_dict = self.init_user_score()
        # self.item_sim = self.item_similarity()
        self.item_sim = self.item_similarity_best()

    def init_user_score(self):
        """
        初始化用户评分数据
        :return:
        """
        user_score_dict = {
            'A': {
                'a': 3.0,
                'b': 4.0,
                'c': 0.0,
                'd': 3.5,
                'e': 0.0
            },
            'B': {
                'a': 4.0,
                'b': 0.0,
                'c': 4.5,
                'd': 0.0,
                'e': 3.5
            },
            'C': {
                'a': 0.0,
                'b': 3.5,
                'c': 0.0,
                'd': 0.0,
                'e': 3.0
            },
            'D': {
                'a': 0.0,
                'b': 4.0,
                'c': 0.0,
                'd': 3.5,
                'e': 3.0
            }
        }

        self.logger.info(user_score_dict)
        return user_score_dict

    def item_similarity(self):
        """
        计算item之间的相似度
        :return:
        """
        item_sim = dict()
        # 得到每个物品有多少用户产生过行为, 每个物品在多少用户中出现
        item_user_count = dict()
        # 同现矩阵，物品i和物品j共同出现的次数
        count = dict()

        for user, item in self.user_score_dict.items():
            for i in item.keys():
                item_user_count.setdefault(i, 0)
                if self.user_score_dict[user][i] > 0.0:
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
                    if self.user_score_dict[user][i] > 0.0 and self.user_score_dict[user][j] > 0.0 and i != j:
                        count[i][j] += 1

        # 同现矩阵 -> 相似度矩阵
        for i, related_items in count.items():
            item_sim.setdefault(i, {})
            for j, cuv in related_items.items():
                item_sim[i].setdefault(j, 0)
                # 物品i和j的相似度定义为：物品i和j共同出现的次数除以物品i出现的总次数
                item_sim[i][j] = cuv / item_user_count[i]

        self.logger.info(json.dumps(item_sim, indent=2, ensure_ascii=False))
        return item_sim

    def item_similarity_best(self):
        """
        计算item之间的相似度, 惩罚热门物品
        :return:
        """
        item_sim = dict()
        # 得到每个物品有多少用户产生过行为, 每个物品在多少用户中出现
        item_user_count = dict()
        # 同现矩阵，物品i和物品j共同出现的次数
        count = dict()

        for user, item in self.user_score_dict.items():
            for i in item.keys():
                item_user_count.setdefault(i, 0)
                if self.user_score_dict[user][i] > 0.0:
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
                    if self.user_score_dict[user][i] > 0.0 and self.user_score_dict[user][j] > 0.0 and i != j:
                        count[i][j] += 1

        # 同现矩阵 -> 相似度矩阵
        for i, related_items in count.items():
            item_sim.setdefault(i, {})
            for j, cuv in related_items.items():
                item_sim[i].setdefault(j, 0)
                # 物品i和j的相似度定义为：物品i和j共同出现的次数除以物品i出现的总次数
                item_sim[i][j] = cuv / math.sqrt(item_user_count[i] * item_user_count[j])

        self.logger.info(json.dumps(item_sim, indent=2, ensure_ascii=False))
        return item_sim

    def pre_user_item_score(self, user, item):
        """
        预测用户对item的评分
        :param user: 用户
        :param item: 物品
        :return:
        """
        score = 0.0
        for item1 in self.item_sim[item].keys():
            if item1 != item:
                score += self.item_sim[item][item1] * self.user_score_dict[user][item1]

        return score

    def recommend(self, user):
        """
        为用户推荐物品
        :param user:
        :return:
        """
        # 计算user未评分item的可能评分
        user_item_score_dict = dict()
        for item in self.user_score_dict[user].keys():
            if self.user_score_dict[user][item] <= 0:
                user_item_score_dict[item] = self.pre_user_item_score(user, item)

        return user_item_score_dict


if __name__ == '__main__':
    logger = get_logger('item_cf')
    ib = ItemCF(logger=logger)
    logger.info(ib.recommend('C'))
    logger.info(ib.recommend('A'))



