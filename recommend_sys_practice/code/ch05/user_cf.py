#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2020/5/4 11:52
# @Author  : yuxuecheng
# @Contact : jayce123@163.com
# @Site    : 
# @File    : user_cf.py
# @Software: PyCharm
# @Description: 基于用户的协同过滤算法示例

import math


class UserCF(object):
    """
    基于用户的协同过滤算法
    """
    def __init__(self):
        self.user_score_dict = self.init_user_score()
        self.users_sim = self.user_similarity_best()

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

        return user_score_dict

    def user_similarity(self):
        """
        计算用户之间的相似度，采用的是遍历每一个用户进行计算
        :return:
        """
        w = dict()
        for u in self.user_score_dict.keys():
            w.setdefault(u, {})
            for v in self.user_score_dict.keys():
                if u == v:
                    continue
                # 用户u评价的物品集合
                u_set = set([key for key in self.user_score_dict[u].keys() if self.user_score_dict[u][key] > 0])
                # 用户v评价的物品集合
                v_set = set([key for key in self.user_score_dict[v].keys() if self.user_score_dict[v][key] > 0])
                # 用户相似度即用户u和用户v评价的物品的交集除以用户u评价物品数和用户v评价物品数的乘积的平方根
                # Wuv = |N(u)N(v)|/sqrt(|N(u)||N(v)|)
                w[u][v] = float(len(u_set & v_set)) / math.sqrt(len(u_set) * len(v_set))

        return w

    def user_similarity_better(self):
        """
        计算用户之间的相似度，采用优化算法时间复杂度的方法
        （1）建立物品到用户的倒排表T,表示该物品被哪些用户产生过行为
        （2）根据倒排表T，建立用户相似度矩阵W
            1. 在T中，对于每个物品i，设其对应的用户为j、k
            2. 在W中，更新对应位置的元素值，W[j][k] = W[j][k] + 1,W[k][j] = W[k][j] + 1
        以此类推，扫描完倒排表T之后，就能得到一个完整的用户相似度矩阵W了。
        :return:
        """
        # 得到每个item被哪些user评价过
        item_users = dict()
        for u, items in self.user_score_dict.items():
            for i in items.keys():
                item_users.setdefault(i, set())
                if self.user_score_dict[u][i] > 0:
                    item_users[i].add(u)

        # 构建倒排表
        C = dict()
        N = dict()
        for i, users in item_users.items():
            for u in users:
                N.setdefault(u, 0)
                N[u] += 1
                C.setdefault(u, {})
                for v in users:
                    C[u].setdefault(v, 0)
                    if u == v:
                        continue
                    C[u][v] += 1

        print(C)
        # {'B': {'B': 0, 'A': 1, 'C': 1, 'D': 1}, 'A': {'B': 1, 'A': 0, 'C': 1, 'D': 2},
        # 'C': {'C': 0, 'D': 2, 'A': 1, 'B': 1}, 'D': {'C': 2, 'D': 0, 'A': 2, 'B': 1}}
        print(N)
        # {'B': 3, 'A': 3, 'C': 2, 'D': 3}

        # 构建相似度矩阵
        w = dict()
        for u, related_users in C.items():
            w.setdefault(u, {})
            for v, cuv in related_users.items():
                if u == v:
                    continue
                w[u].setdefault(v, 0.0)
                w[u][v] = cuv / math.sqrt(N[u] * N[v])
        return w

    def user_similarity_best(self):
        """
        在使用倒排表的基础上，再加入对于热门物品的惩罚因子
        :return:
        """
        # 得到每个item被哪些user评价过
        item_users = dict()
        for u, items in self.user_score_dict.items():
            for i in items.keys():
                item_users.setdefault(i, set())
                if self.user_score_dict[u][i] > 0:
                    item_users[i].add(u)

        # 构建倒排表
        C = dict()
        N = dict()
        for i, users in item_users.items():
            for u in users:
                N.setdefault(u, 0)
                N[u] += 1
                C.setdefault(u, {})
                for v in users:
                    C[u].setdefault(v, 0)
                    if u == v:
                        continue
                    C[u][v] += 1 / math.log(1+len(users))

        print(C)
        # {'A': {'A': 0, 'B': 0.9102392266268373, 'C': 0.7213475204444817, 'D': 1.631586747071319},
        # 'B': {'A': 0.9102392266268373, 'B': 0, 'C': 0.7213475204444817, 'D': 0.7213475204444817},
        # 'C': {'A': 0.7213475204444817, 'C': 0, 'D': 1.4426950408889634, 'B': 0.7213475204444817},
        # 'D': {'A': 1.631586747071319, 'C': 1.4426950408889634, 'D': 0, 'B': 0.7213475204444817}}
        print(N)
        # {'A': 3, 'B': 3, 'C': 2, 'D': 3}

        # 构建相似度矩阵
        w = dict()
        for u, related_users in C.items():
            w.setdefault(u, {})
            for v, cuv in related_users.items():
                if u == v:
                    continue
                w[u].setdefault(v, 0.0)
                w[u][v] = cuv / math.sqrt(N[u] * N[v])
        return w

    def pre_user_item_score(self, user_a, item):
        """
        预测用户对item的评分
        :param user_a: 用户
        :param item:
        :return:
        """
        score = 0.0
        for user in self.users_sim[user_a].keys():
            if user != user_a:
                score += self.users_sim[user_a][user] * self.user_score_dict[user][item]

        return score

    def recommend(self, user_a):
        """
        为用户推荐物品
        :param user_a:
        :return:
        """
        # 计算user_a未评分item的可能评分
        user_item_score_dict = {}
        for item in self.user_score_dict[user_a].keys():
            if self.user_score_dict[user_a][item] <= 0:
                # 如果评分小于等于0，说明没有评分记录，则计算可能得评分
                user_item_score_dict[item] = self.pre_user_item_score(user_a, item)

        return user_item_score_dict


if __name__ == '__main__':
    ucf = UserCF()
    print(f'用户B推荐：{ucf.recommend("B")}')
    print(f'用户C推荐：{ucf.recommend("C")}')
