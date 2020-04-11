#!/usr/bin/env python3
# encoding: utf-8

"""
@version: 1.0
@author: ‘yuxuecheng‘
@contact: yuxuecheng@baicdata.com
@software: PyCharm Community Edition
@file: UserCF.py
@time: 04/01/2018 08:43
"""

import random
import math
import operator


def split_data(data, M, k, seed):
    """
    将数据集随机分成训练集和测试集，每次实验选取不同的k(0 <= k <= M-1)和相同的随机数种子
    进行M次实验就可以得到M个不同的训练集和测试集

    :param data: 总数据集
    :param M: 需要进行的实验次数
    :param k: 随机选择的一份测试集
    :param seed: 随机数种子
    :return: 训练集和测试集
    """
    test = dict()
    train = dict()
    random.seed(seed)
    for user, item in data:
        if random.randint(0, M) == k:
            test.setdefault(user, []).append(item)
        else:
            train.setdefault(user, []).append(item)

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


def user_similarity(train):
    W = dict()
    for u in train.keys():
        for v in train.keys():
            if u == v:
                continue
            W[u][v] = len(train[u] & train[v])
            W[u][v] /= math.sqrt(len(train[u]) * len(train[v]) * 1.0)

    return W


def user_similarity_v2(train):
    # build inverse table for item_users
    item_users = dict()
    for u, items in train.items():
        for i in items.keys():
            if i not in item_users:
                item_users[i] = set()
            item_users[i].add(u)

    # calculate co-rated items between users
    C = dict()
    N = dict()
    for i, users in item_users.items():
        for u in users:
            N[u] += 1
            for v in users:
                if u == v:
                    continue
                C[u][v] += 1

    # calculate finial similarity matrix W
    W = dict()
    for u, related_users in C.items():
        for v, cuv in related_users.items():
            W[u][v] = cuv / math.sqrt(N[u] * N[v])

    return W


def user_similarity_v3(train):
    # build inverse table for item_users
    item_users = dict()
    for u, items in train.items():
        for i in items:
            if i not in item_users:
                item_users[i] = set()
            item_users[i].add(u)

    # calculate co-rated items between users
    C = dict()
    N = dict()
    for i, users in item_users.items():
        for u in users:
            if u not in N:
                N[u] = 0
            N[u] += 1
            for v in users:
                if u == v:
                    continue
                if u not in C:
                    C[u] = dict()
                    C[u][v] = 0
                elif v not in C[u]:
                    C[u][v] = 0
                C[u][v] += 1 / math.log(1 + len(users))

    # print(N)
    # calculate finial similarity matrix W
    W = dict()
    for u, related_users in C.items():
        for v, cuv in related_users.items():
            if not u in W:
                W[u] = dict()
            W[u][v] = cuv / math.sqrt(N[u] * N[v])

    return W


def get_recommendation(user, train, N):
    W = user_similarity_v3(train)
    rank = dict()

    return rank


def recommend(user, train, W, K):
    rank = dict()
    interacted_items = train[user]
    for v, wuv in sorted(W.items(), key=operator.itemgetter(1), reverse=True)[0:K]:
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
    first = True
    with open(movie_file_name, mode='r') as fd:
        for line in fd:
            if first:
                first = False
                continue
            line = line.strip()
            segs = [seg.strip() for seg in line.split(sep=',', maxsplit=3)]
            movies[segs[0]] = segs[1]

    # print(movies)
    first = True
    ratings_file_name = "/Users/yuxuecheng/Documents/Recommendation/data/ml-20m/ratings.csv"
    number = 0
    with open(ratings_file_name, mode='r') as fd:
        for line in fd:
            if first:
                first = False
                continue
            if number > 10000:
                break
            number += 1
            line = line.strip()
            segs = [seg.strip() for seg in line.split(sep=',', maxsplit=4)]
            user_movies.append((segs[0], segs[1]))

    train, test = split_data(user_movies, 10, 1, 1000)
    # print("train data:")
    # print(train)
    # print("test data:")
    # print(test)

    W = user_similarity_v3(train)
    print(W["1"])
    rank = recommend("1", train, W, K=5)
    print(rank)