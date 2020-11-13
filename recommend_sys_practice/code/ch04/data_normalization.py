#!/usr/bin/env python3
'''
@File    :   data_normalization.py
@Time    :   2020/04/23 16:48:02
@Author  :   Yu Xuecheng 
@Version :   1.0
@Contact :   yuxuecheng@xinluomed.com
@License :   (C)Copyright 2020-2022, yuxuecheng
@Desc    :   本源码文件是进行数据标准化的方法，代码参考《推荐系统开发实战》 4.1.2章节
'''

# here put the import lib
import numpy as np
import math


class DataNorm(object):
    def __init__(self, arr=[1, 2, 3, 4, 5, 6, 7, 8]):
        super().__init__()
        self.np_arr = None
        if isinstance(arr, np.ndarray):
            self.np_arr = arr
        elif isinstance(arr, list) or isinstance(arr, range):
            self.np_arr = np.array(arr)
        else:
            print('参数错误')
            return
        self.x_max = self.np_arr.max()  # 最大值
        self.x_min = self.np_arr.min()  # 最小值
        self.x_mean = self.np_arr.mean()  # 平均值
        self.x_std = self.np_arr.std()  # 标准差

    def __repr__(self):
        return f'数据列表: {self.np_arr}, \n最大值: {self.x_max}, 最小值: {self.x_min}, 平均值: {self.x_mean}, 标准差: {self.x_std}'

    def min_max(self):
        arr_ = list()
        for x in self.np_arr:
            # round(x, 4) 对x保留4位小数
            arr_.append(round((x-self.x_min) / (self.x_max - self.x_min), 4))
        print(f'经过min_max标准化后的数据为：\n{arr_}')

    def z_score(self):
        """
        Z-Score标准化：基于原始数据的均值和标准差来进行数据的标准化。
        :return:
        """
        arr_ = list()
        for x in self.np_arr:
            arr_.append(round((x - self.x_mean) / self.x_std, 4))
        print(f'经过z_score标准化后的数据为：\n{arr_}')

    def decimal_scaling(self):
        """
        小数定标（Decimal Scaling）标准化：通过移动小数点的位置来进行数据的标准化。小数
        点移动的位数取决于原始数据中的最大绝对值。
        :return:
        """
        arr_ = list()
        j = 1
        # 获取绝对值的最大值
        x_max = max([abs(one) for one in self.np_arr])

        # 获取最大值是10的多少次方
        while x_max / 10 >= 1.0:
            j += 1
            x_max = x_max / 10

        for x in self.np_arr:
            arr_.append(round(x / math.pow(10, j), 4))

        print(f'经过decimal_scaling标准化后的数据为：\n{arr_}')

    def mean(self):
        """
        均值归一化：通过原始数据中的均值、最大值和最小值来进行数据的标准化。
        :return:
        """
        arr_ = list()
        for x in self.np_arr:
            # round(x, 4) 对x保留4位小数
            arr_.append(round((x-self.x_mean) / (self.x_max - self.x_min), 4))
        print(f'经过mean标准化后的数据为：\n{arr_}')

    def vector(self):
        """
        向量归一化：通过对原始数据中的每个值除以所有数据之和来进行数据的标准化。
        :return:
        """
        arr_ = list()
        arr_sum = self.np_arr.sum()
        for x in self.np_arr:
            # round(x, 4) 对x保留4位小数
            arr_.append(round(x / arr_sum, 4))
        print(f'经过vector标准化后的数据为：\n{arr_}')

    def exponential(self):
        """
        指数转换是指通过对原始数据的值进行相应的指数函数变换来进行数据的标准化。
        进行指数转换常见的函数方法有lg函数，softmax函数和sigmoid函数
        :return:
        """
        arr_1 = list()
        for x in self.np_arr:
            # round(x, 4) 对x保留4位小数
            arr_1.append(round(math.log10(x) / math.log10(self.x_max), 4))
        print(f'经过指数转换法（log10）标准化后的数据为：\n{arr_1}')

        arr_2 = list()
        sum_e = sum([math.exp(one) for one in self.np_arr])
        for x in self.np_arr:
            # round(x, 4) 对x保留4位小数
            arr_2.append(round(math.exp(x) / sum_e, 4))
        print(f'经过指数转换法（softmax）标准化后的数据为：\n{arr_2}')

        arr_3 = list()
        for x in self.np_arr:
            # round(x, 4) 对x保留4位小数
            arr_3.append(round(1 / (1 + math.exp(-x)), 4))
        print(f'经过指数转换法（sigmoid）标准化后的数据为：\n{arr_3}')


if __name__ == "__main__":
    arr = range(1, 100, 2)
    data_norm = DataNorm(arr=arr)
    print(data_norm)
    # data_norm = DataNorm(arr='aaa')
    # print(data_norm)
    data_norm.min_max()
    data_norm.z_score()
    data_norm.decimal_scaling()
    data_norm.mean()
    data_norm.vector()
    data_norm.exponential()
