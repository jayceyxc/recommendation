#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2020/5/4 10:49
# @Author  : yuxuecheng
# @Contact : jayce123@163.com
# @Site    : 
# @File    : content_based_movie_recommend.py
# @Software: PyCharm
# @Description: 基于内容推荐算法的电影推荐系统

import pandas as pd
import json
import codecs
import numpy as np
import math
import random


class DataProcessing(object):
    """
    数据格式转换
    """
    def __init__(self):
        super().__init__()
        self.item_dict = {}
        self.genres_all = None
        self.item_matrix = {}
        self.user_matrix = {}

    def process(self):
        print('开始转换用户数据(users.data)...')
        self.process_user_data()
        print('开始转换电影数据(movies.data)...')
        self.process_movies_data()
        print('开始转换评分数据(ratings.data)...')
        self.process_rating_data()
        print('转换完成')

    def process_user_data(self, file='../../data/ml-1m/users.dat'):
        """
        处理用户数据
        :param file:
        :return:
        """
        fp = pd.read_table(file, sep='::', engine='python', names=['UserID', 'Gender', 'Age', 'Occupation', 'Zip-code'])
        fp.to_csv('data/users.csv', index=False)

    def process_rating_data(self, file='../../data/ml-1m/ratings.dat'):
        """
        处理评分数据
        :param file:
        :return:
        """
        fp = pd.read_table(file, sep='::', engine='python', names=['UserID', 'MovieID', 'Rating', 'TimeStamp'])
        fp.to_csv('data/ratings.csv', index=False)

    def process_movies_data(self, file='../../data/ml-1m/movies.dat'):
        """
        处理电影数据
        :param file:
        :return:
        """
        fp = pd.read_table(file, sep='::', engine='python', names=['MovieID', 'Title', 'Genres'])
        fp.to_csv('data/movies.csv', index=False)

    def prepare_item_profile(self, file='data/movies.csv'):
        """
        计算电影的特征信息矩阵，并保存在文件中
        :param file:
        :return:
        """
        items = pd.read_csv(file)
        item_ids = set(items['MovieID'].values)
        genres_all = list()

        # 将每个电影的类型放在item_dict中
        for item in item_ids:
            genres = items[items['MovieID'] == item]['Genres'].values[0].split('|')
            self.item_dict.setdefault(item, []).extend(genres)
            genres_all.extend(genres)

        self.genres_all = set(genres_all)

        genres_all_list = list(self.genres_all)
        # 将每个电影的特征信息矩阵存放在self.item_matrix中
        for item in self.item_dict.keys():
            self.item_matrix[str(item)] = [0] * len(self.genres_all)
            for genre in self.item_dict[item]:
                index = genres_all_list.index(genre)
                self.item_matrix[str(item)][index] = 1

        save_path = 'data/item_profile.json'
        json.dump(self.item_matrix, codecs.open(save_path, mode='w', encoding='utf8'))
        print(f'item 信息计算完成, 保存路径为：{save_path}')

    def prepare_user_profile(self, file='data/ratings.csv'):
        """
        计算用户的偏好矩阵，并保存在文件中
        :param file:
        :return:
        """
        users = pd.read_csv(file)
        user_ids = set(users['UserID'].values)

        # 将users信息转换成dict
        users_rating_dict = {}
        for user in user_ids:
            users_rating_dict.setdefault(str(user), {})

        with codecs.open(file, mode='r', encoding='utf8') as fr:
            for line in fr.readlines():
                if not line.startswith('UserID'):
                    (user, item, rate) = line.split(',')[:3]
                    users_rating_dict[user][item] = int(rate)

        # 获取用户对每个类型下的哪些电影进行了评分
        for user in users_rating_dict.keys():
            print(f'user is {user}')
            score_list = users_rating_dict[user].values()
            # 用户的平均打分
            avg = sum(score_list) / len(score_list)
            self.user_matrix[user] = []
            # 遍历每个类型，保证item_profile和user_profile信息矩阵中没列表式的类型一致
            for genre in self.genres_all:
                score_all = 0.0
                score_len = 0
                # 遍历每个item
                for item in users_rating_dict[user].keys():
                    # 判断类型是否在用户评分过的电影里
                    if genre in self.item_dict[int(item)]:
                        score_all += (users_rating_dict[user][item] - avg)
                        score_len += 1

                if score_len == 0:
                    self.user_matrix[user].append(0.0)
                else:
                    self.user_matrix[user].append(score_all / score_len)

        save_path = 'data/user_profile.json'
        json.dump(self.user_matrix, codecs.open(save_path, mode='w', encoding='utf8'))
        print(f'user 信息计算完成，保存路径为 {save_path}')


class CBMovieRecommend(object):
    """
    基于内容推荐的推荐类
    """
    def __init__(self, K):
        # 加载DataProcessing中预处理的数据
        super().__init__()
        # 给用户推荐的item个数
        self.K = K
        self.item_profile = json.load(codecs.open('data/item_profile.json', mode='r', encoding='utf8'))
        self.user_profile = json.load(codecs.open('data/user_profile.json', mode='r', encoding='utf8'))
        self.items = pd.read_csv('data/movies.csv')
        self.ratings = pd.read_csv('data/ratings.csv')

    def get_none_score_item(self, user):
        """
        获取用户未进行评分的item列表
        :param user:
        :return:
        """
        items = self.items['MovieID'].values
        have_score_items = self.ratings[self.ratings['UserID'] == user]['MovieID'].values
        none_score_items = set(items) - set(have_score_items)
        return none_score_items

    def cosUI(self, user, item):
        """
        获取用户对item的喜好程度
        :param user: 用户ID
        :param item: 物品ID
        :return:
        """
        Uia = sum(
            np.array(self.user_profile[str(user)])
            *
            np.array(self.item_profile[str(item)])
        )
        Ua = math.sqrt(sum([math.pow(one, 2) for one in self.user_profile[str(user)]]))
        Ia = math.sqrt(sum([math.pow(one, 2) for one in self.item_profile[str(item)]]))
        return Uia / (Ua * Ia)

    def recommend(self, user):
        """
        为用户进行电影推荐
        :param user:
        :return:
        """
        user_result = {}
        item_list = self.get_none_score_item(user)
        for item in item_list:
            user_result[item] = self.cosUI(user, item)

        if self.K is None:
            result = sorted(user_result.items(), key=lambda k:k[1], reverse=True)
        else:
            result = sorted(user_result.items(), key=lambda k:k[1], reverse=True)[:self.K]

        print(result)

    def evaluate(self):
        """
        推荐效果评估
        这里采用的评估方法是：给用户推荐的电影和用户本身评分电影的交集与用户本身评分电影的数目比
        :return:
        """
        evas = []
        data = pd.read_csv('data/ratings.csv')
        # 随机选取20个用户进行效果评估
        random_user = random.sample([one for one in range(1, 6401)], 20)
        for user in random_user:
            have_scored_items = data[data['UserID'] == user]['MovieID'].values
            items = pd.read_csv('data/movies.csv')['MovieID'].values
            user_result = {}
            for item in items:
                user_result[item] = self.cosUI(user, item)

            results = sorted(user_result.items(), key=lambda k:k[1], reverse=True)[:len(have_scored_items)]
            rec_items = []
            for one in results:
                rec_items.append((one[0]))

            eva = len(set(rec_items) & set(have_scored_items)) / len(have_scored_items)
            evas.append(eva)

        return sum(evas) / len(evas)


if __name__ == '__main__':
    # data_process = DataProcessing()
    # data_process.process()
    # data_process.prepare_item_profile()
    # data_process.prepare_user_profile()
    cb = CBMovieRecommend(K=10)
    cb.recommend(user=100)
    print(f'推荐评估结果：{cb.evaluate()}')
