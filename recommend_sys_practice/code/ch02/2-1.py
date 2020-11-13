#!/usr/bin/env python3
'''
@File    :   2-1.py
@Time    :   2020/04/22 10:54:20
@Author  :   Yu Xuecheng 
@Version :   1.0
@Contact :   yuxuecheng@xinluomed.com
@License :   (C)Copyright 2020-2022, yuxuecheng
@Desc    :   第一个推荐系统
'''

# here put the import lib
import os
import json
import random
import math


class FirstRec(object):
    def __init__(self, file_path, seed, k, n_items):
        """
        初始化函数
        @param file_path: 原始文件路径
        @param seed: 产生随机数的种子
        @param k: 选取的近邻用户个数
        @param n_items: 为每个用户推荐的电影数
        """
        super().__init__()
        self.train_json_path = 'recommend_sys_practice/code/ch02/data/train.json'
        self.test_json_path = 'recommend_sys_practice/code/ch02/data/test.json'
        self.file_path = file_path
        self.users_1000 = self.select_1000_users()
        self.seed = seed
        self.k = k
        self.n_items = n_items
        self.train, self.test = self.load_and_split_data()

    def select_1000_users(self):
        """
        获取所有用户并随机选取1000个用户
        """
        print('随机选取1000个用户！')
        if os.path.exists(self.train_json_path) and os.path.exists(self.test_json_path):
            return list()
        else:
            users = set()
            # 获取所有用户
            for file in os.listdir(self.file_path):
                one_path = os.path.join(self.file_path, file)
                print(f'{one_path}')
                with open(one_path, mode='r') as fp:
                    for line in fp.readlines():
                        if line.strip().endswith(':'):
                            continue
                        userId, _, _ = line.split(',')
                        users.add(userId)

            # 随机选取1000个
            users_1000 = random.sample(list(users), 1000)
            print(users_1000)
            return users_1000

    def load_and_split_data(self):
        train = dict()
        test = dict()
        if os.path.exists(self.train_json_path) and os.path.exists(self.test_json_path):
            print('从文件中加载训练集和测试集')
            with open(self.train_json_path) as fp:
                train = json.load(fp)
            with open(self.test_json_path) as fp:
                test = json.load(fp)
            print('从文件中加载数据完成')
        else:
            # 设置产生随机数的种子，保证每次实验产生的随机结果一致
            random.seed(self.seed)
            for file in os.listdir(self.file_path):
                one_path = os.path.join(self.file_path, file)
                print(f'{one_path}')
                with open(one_path, mode='r') as fp:
                    movieID = fp.readline().split(':')[0]
                    for line in fp.readlines():
                        if line.endswith(':'):
                            continue

                        userId, rate, _ = line.split(',')
                        # 判断用户是否在所选择的1000个用户中
                        if userId in self.users_1000:
                            if random.randint(1, 50) == 1:
                                test.setdefault(userId, {})[
                                    movieID] = int(rate)
                            else:
                                train.setdefault(userId, {})[
                                    movieID] = int(rate)

            print(f'加载数据到{self.train_json_path}和{self.test_json_path}')
            json.dump(train, open(self.train_json_path, 'w'))
            json.dump(test, open(self.test_json_path, 'w'))
            print('加载数据完成')

        return train, test

    def pearson(self, rating1, rating2):
        """
        计算皮尔逊相关系数
        rating1: 用户1的评分记录，形式如{"movieId1": rate1, "movieId2": rate2}
        rating2: 用户2的评分记录，形式如{"movieId1": rate1, "movieId2": rate2}
        """
        if not isinstance(rating1, dict) or not isinstance(rating2, dict):
            return

        sum_xy = 0
        sum_x = 0
        sum_y = 0
        sum_x2 = 0
        sum_y2 = 0
        num = 0
        for key in rating1.keys():
            for key in rating2.keys():
                num += 1
                x = rating1[key]
                y = rating2[key]
                sum_xy += x * y
                sum_x += x
                sum_y += y
                sum_x2 += math.pow(x, 2)
                sum_y2 += math.pow(y, 2)

        if num == 0:
            return 0

        # 皮尔逊相关系数的分母
        denominator = math.sqrt(sum_x2 - math.pow(sum_x, 2) / num) * \
            math.sqrt(sum_y2 - math.pow(sum_y, 2) / num)
        if denominator == 0:
            return 0
        else:
            return (sum_xy - sum_x * sum_y / num) / denominator

    def recommend(self, user_id):
        """
        对用户进行电影推荐
        user_id: 用户ID
        """
        neighborUser = dict()
        for user in self.train.keys():
            if user_id != user:
                distance = self.pearson(self.train[user_id], self.train[user])
                neighborUser[user] = distance

        # 字典排序，按distance进行排序
        newNU = sorted(neighborUser.items(), key=lambda k: k[1], reversed=True)

        movies = dict()
        for (sim_user, sim) in newNU[: self.k]:
            for movie_id in self.train[sim_user].keys():
                movies.setdefault(movie_id, 0)
                movies[movie_id] += sim * self.train[sim_user][movie_id]

        newMovies = sorted(movies.items(), key=lambda k: k[1], reversed=True)

        return newMovies

    def evaluate(self, num=30):
        """
        推荐系统效果评估函数
        评估方法：针对测试集，为其推荐的电影占其本身有行为电影的比例
        num: 随机选取 num 个用户计算准确率
        """
        print('开始计算准确率')
        precisions = list()
        random.seed(10)
        for user_id in random.sample(self.test.keys(), num):
            hit = 0
            result = self.recommend(user_id=user_id)[: self.n_items]
            for (item, rate) in result:
                if item in self.test[user_id]:
                    hit += 1

            precisions.append(hit / self.n_items)
        return sum(precisions) / precisions.__len__()


# main函数，程序的入口
if __name__ == "__main__":
    file_path = 'recommend_sys_practice/data/netflix/training_set'
    seed = 30
    k = 15
    n_items = 20
    f_rec = FirstRec(file_path=file_path, seed=seed, k=k, n_items=n_items)

    # 计算用户 195100 和 1547579 的皮尔逊相关系数
    # r = f_rec.pearson(f_rec.train['195100'], f_rec.train['1547579'])
    # print(f'195100 和 1547579 的皮尔逊相关系数为: {r}')

    # 为用户 195100 进行电影推荐
    # result = f_rec.recommend('195100')
    # print(result)

    # 计算准确率
    # print(f'算法的推荐准确率为：{f_rec.evaluate()}')
