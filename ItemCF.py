#!/usr/bin/env python3
# encoding: utf-8

"""
@version: 1.0
@author: ‘yuxuecheng‘
@contact: yuxuecheng@baicdata.com
@software: PyCharm Community Edition
@file: ItemCF.py
@time: 05/01/2018 14:45
"""

import random
import math
import operator


def split_data(data, M, k, seed):
    """
    将数据集随机分成训练集和测试集，每次实验选取不同的k(0 <= k <= M-1)和相同的随机数种子
    进行M次实验就可以得到M个不同的训练集和测试集

    In [14]: data = []

    In [15]: data.append(('1', 'test'))

    In [16]: data.append(('2', 'test2'))

    In [17]: for user, item in data:
        ...:     print(user, item)
        ...:
    1 test
    2 test2

    :param data: 总数据集, 是用户id和物品id组成的元组组成的列表
    :param M: 需要进行的实验次数
    :param k: 随机选择的一份测试集
    :param seed: 随机数种子
    :return: 训练集和测试集
    """
    test = []
    train = []
    random.seed(seed)
    for user, item in data:
        if random.randint(0, M) == k:
            test.append([user, item])
        else:
            train.append([user, item])

    return train, test


def recall(train, test, N):
    """
    计算召回率，召回率描述有多少比例的用户-物品评分记录包含在最终的推荐中
    :param train:
    :param test:
    :param N:
    :return:
    """
    hit = 0
    all = 0
    for user in train.keys():
        tu = test[user]
        rank = get_recommendation(user, N)
        for item, pui in rank:
            if item in tu:
                hit += 1

        all += len(tu)
    return hit / (all * 1.0)


def precision(train, test, N):
    """
    计算准确率，准确率描述最终的推荐列表中有多少比例是发生过的用户-物品评分记录
    :param train:
    :param test:
    :param N:
    :return:
    """
    hit = 0
    all = 0
    for user in train.keys():
        tu = test[user]
        rank = get_recommendation(user, N)
        for item, pui in rank:
            if item in tu:
                hit += 1
        all += N

    return hit / (all * 1.0)


def coverage(train, test, N):
    """
    计算覆盖率，覆盖率反映了推荐算法发掘长尾的能力，覆盖率越高，说明推荐算法越能够将长尾
    中的物品推荐给用户
    :param train:
    :param test:
    :param N:
    :return:
    """
    recommend_items = set()
    all_items = set()
    for user in train.keys():
        for item in train[user].keys():
            all_items.add(item)
        rank = get_recommendation(user, N)
        for item, pui in rank:
            recommend_items.add(item)

    return len(recommend_items) / (len(all_items) * 1.0)


def popularity(train, test, N):
    item_popularity = dict()
    for user, items in train.items():
        for item in items.keys():
            if item not in item_popularity:
                item_popularity[item] = 0
            item_popularity[item] += 1

    ret = 0
    n = 0
    for user in train.keys():
        rank = get_recommendation(user, N)
        for item, pui in rank:
            ret += math.log(1 + item_popularity[item])
            n += 1

    ret /= n * 1.0
    return ret


def item_similarity(train):
    # calculate co-rated users between items
    C = dict()
    N = dict()
    for u, items in train.items():
        for i in items:
            pass


def get_recommendation(user, N):
    rank = dict()

    return rank


def recommend(user, train, W):
    rank = dict()
    interacted_items = train[user]
    for v, wuv in sorted(W.items(), key=operator.itemgetter(1), reverse=True)[0:10]:
        for i, rvi in train[v].items():
            if i in interacted_items:
                # We should filter items user interacted before
                continue
            rank[i] += wuv * rvi
    return rank


if __name__ == '__main__':
    user_movies = []
    movies = dict()
    movie_file_name = "/Users/yuxuecheng/Documents/Recommendation/data/ml-20m/movies.csv"
    with open(movie_file_name, mode='r') as fd:
        for line in fd:
            line = line.strip()
            segs = [seg.strip() for seg in line.split(',', maxsplit=3)]
            movies[segs[0]] = segs[1]

    print(movies)

    ratings_file_name = "/Users/yuxuecheng/Documents/Recommendation/data/ml-20m/ratings.csv"
    with open (ratings_file_name, mode='r') as fd:
        for line in fd:
            line = line.strip()
            segs = [seg.strip() for seg in line.split(',', maxsplit=4)]
            user_movies.append((segs[0], segs[1]))

    train, test = split_data(user_movies, 10, 1, 1000)
