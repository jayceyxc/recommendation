#!/usr/bin/env python3
'''
@File    :   apriori.py
@Time    :   2020/05/03 17:11:19
@Author  :   Yu Xuecheng 
@Version :   1.0
@Contact :   yuxuecheng@xinluomed.com
@License :   (C)Copyright 2020-2022, yuxuecheng
@Desc    :   基于APriori算法实现频繁项集合相关规则挖掘
'''

# here put the import lib


class Apriori(object):
    """
    基于APriori算法实现频繁项集合相关规则挖掘
    """

    def __init__(self, min_support, min_confidence):
        super().__init__()
        # 最小支持度
        self.min_support = min_support
        # 最小置信度
        self.min_confidence = min_confidence
        self.data = self.load_data()

    def load_data(self):
        """
        加载数据集
        """
        return [[1, 5], [2, 3, 4], [2, 3, 4, 5], [2, 3]]

    def create_c1(self, data):
        """
        生成项集C1，不包含相机中每个元素出现的次数
        :return:
        """
        # c1为大小为1的项的集合
        c1 = list()
        for items in data:
            for item in items:
                if [item] not in c1:
                    c1.append([item])

        # map函数表示遍历c1中的每个元素执行frozenset
        # frozenset表示“冰冻”集合，即不可改变
        return list(map(frozenset, sorted(c1)))

    # 生成频繁项集
    """
    根据生成的初始项集，依次生成包含更多项的项集，并过滤掉不满足最小支持度的项集，得到最终结果
    1. 扫描初始候选项集c1，生成项集l1和所有的项集组合support_data
    2. 将项集l1加入l中进行记录，l为每次迭代后符合支持度的项集
    3. 根据l1生成新的候选项集c2；
    4。 扫描候选项集c2，生成项集l2和所有的项集集合
    5. 更新项集合support_data和l
    6. 重复步骤（2）-（5），直到项集中的元素为全部元素时停止迭代。
    """
    def scand(self, ck):
        """
        该函数用于从候选集ck生成lk，lk表示满足最低支持度的元素集合
        :param ck:
        :return:
        """
        # data表示数据列表的列表，[set([]), set([]), set([]), set([])]
        data = list(map(set, self.data))
        ck_count = {}
        for items in data:
            for one in ck:
                # issubset: 表示如果集合one中的每一个元素都在items中，则返回true
                if one.issubset(items):
                    ck_count.setdefault(one, 0)
                    ck_count[one] += 1

        # 数据条数
        num_items = len(list(data))
        # 初始化符合支持度的项集
        lk = []
        # 初始化所有符合条件的项集及对应的支持度
        support_data = {}
        for key in ck_count:
            # 计算每个项集的支持度，如果满足条件则把该项集加入到lk列表中
            support = ck_count[key] * 1.0 / num_items
            if support >= self.min_support:
                lk.insert(0, key)

            # 构建支持的项集的字典
            support_data[key] = support

        return lk, support_data

    def generate_new_ck(self, lk, k):
        """

        :param lk: 频繁项集列表
        :param k: 项集元素个数
        :return: ck
        """
        next_lk = []
        len_lk = len(lk)
        # 若两个项集的长度为k-1，则必须前k-2项相同才可连接，即求并集，所以[:k-2]的实际作用为取列表的前k-1个元素
        for i in range(len_lk):
            for j in range(i+1, len_lk):
                # 前k-2项相同时合并两个集合
                l1 = list(lk[i])[: k-2]
                l2 = list(lk[j])[: k-2]
                if sorted(l1) == sorted(l2):
                    next_lk.append(lk[i] | lk[j])

        return next_lk

    # 生成频繁项集
    def genenrate_lk(self):
        # 构建候选项集c1
        c1 = self.create_c1(self.data)
        l1, support_data = self.scand(c1)
        l = [l1]
        k = 2
        while len(l[k-2]) > 0:
            # 组合项集lk中元素，生成新的候选项集ck
            ck = self.generate_new_ck(l[k-2], k)
            lk, support_k = self.scand(ck)
            support_data.update(support_k)
            l.append(lk)
            k += 1

        return l, support_data

    # 生成相关规则
    """
    一旦找到了频繁项集，就可以直接由它们生成相关规则，步骤如下
    1. 对于每个频繁项集itemset，生成itemset的所有非空子集（这些非空子集一定是频繁项集）
    2. 对于itemset的每个非空子集s，如果s的置信度大于设置的最小置信度，则输出对应的相关规则
    """

    def genenrate_rules(self, l, support_data):
        """
        :param l:
        :param support_data:
        :return:
        """
        # 最终记录的相关规则结果
        rule_result = []
        for i in range(1, len(l)):
            for ck in l[i]:
                cks = [frozenset([item]) for item in ck]
                # 频繁项集中有三个及三个以上元素的集合
                self.rules_of_more(ck, cks, support_data, rule_result)

        return rule_result

    def rules_of_two(self, ck, cks, support_data, rules_result):
        """
        频繁项集只有两个元素
        :param ck:
        :param cks:
        :param support_data:
        :param rules_result:
        :return:
        """
        pruned_h = []
        for one_ck in cks:
            # 计算置信度
            conf = support_data[ck] / support_data[ck - one_ck]
            if conf >= self.min_confidence:
                print(ck - one_ck, "-->", one_ck, "confidence is: ", conf)
                rules_result.append((ck - one_ck, one_ck, conf))
                pruned_h.append(one_ck)

        return pruned_h

    def rules_of_more(self, ck, cks, support_data, rules_result):
        """
        频繁项集中有三个及三个以上的元素的集合，递归生成相关规则
        :param ck:
        :param cks:
        :param support_data:
        :param rules_result:
        :return:
        """
        m = len(cks[0])
        while len(ck) > m:
            cks = self.rules_of_two(ck, cks, support_data, rules_result)
            if len(cks) > 1:
                cks = self.generate_new_ck(cks, m+1)
                m += 1
            else:
                break


if __name__ == '__main__':
    apriori = Apriori(min_support=0.5, min_confidence=0.6)
    l, support_data = apriori.genenrate_lk()
    for one in l:
        print(f'项数为 {l.index(one) + 1} 的频繁项集：{one}')

    print(f'support data: {support_data}')
    print(f'min_conf=0.6时:')
    rules = apriori.genenrate_rules(l, support_data)
