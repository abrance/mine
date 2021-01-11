import math
from pprint import pprint


class NumberSet(object):
    def __init__(self):
        # 数独本质是九个列表的集合
        self.data = [[] for _ in range(9)]
        # 倒置(竖)数独，九个列表集合
        self.op_data = [[] for _ in range(9)]
        # 3*3 数独
        self.little_set = [[] for _ in range(3)]
        self.true_data = [[] for _ in range(9)]
        self.stack = []

    def get_little_set(self, axis: tuple):
        x, y = axis
        ls = [self.data[i][(y - 1) * 3: y * 3] for i in range((x - 1) * 3, x * 3)]
        self.little_set = ls
        return ls

    def import_data(self, _data):
        # 导入数独
        self.data = data
        self.operate_data()

    def fill(self):

        self.data = [[i for i in range(1, 10)] for _ in range(9)]

    def operate_data(self):
        # 填充(竖)数独
        self.op_data = list(zip(*self.data))

    def get_space_poss_set(self, axis: tuple):
        # 返回 候选值集合
        # 已经填了值，返回0
        x, y = axis
        if self.data[x-1][y-1] != 0:
            return 0
        else:
            filled_space_x = [i for i in self.data[x-1] if i != 0]
            self.operate_data()
            filled_space_y = [i for i in self.op_data[y-1] if i != 0]
            ls = []
            # ceil 进1取值
            for i in self.get_little_set((math.ceil(x/3), math.ceil(y/3))):
                ls += [j for j in i if j != 0]

            full_set = {i for i in range(1, 10)}
            subtra = lambda _x: full_set - _x
            sub_filled_space_x = subtra(set(filled_space_x))
            sub_filled_space_y = subtra(set(filled_space_y))
            sub_filled_space_x_y = subtra(set(ls))
            poss_filled_set = sub_filled_space_x & sub_filled_space_y & sub_filled_space_x_y
            if poss_filled_set:
                return poss_filled_set
            else:
                return set()

    def fill_fake_data(self, axis, num, last_set):
        self.stack.append((axis, num, last_set))
        x, y = axis
        self.data[x-1][y-1] = num
        return True

    def free_fake_data(self, axis):
        x, y = axis
        self.data[int(x-1)][int(y-1)] = 0
        return True

    def check(self):
        # 挑选出难度最小的空，进行 填空
        # 策略1，get_space_degree_difficulty 返回值为 8 的，可以直接填，因为这是确定值
        # 策略2，三者的补集求交集
        finish = True
        cnt = 0             # 这一轮填的空数，如果填了空，而且还有空，那么一定要再来一轮
        min_set = tuple()

        for x in range(1, 10):
            for y in range(1, 10):
                ret = self.get_space_poss_set((x, y))
                if ret == 0:
                    pass
                elif isinstance(ret, set):
                    if finish:
                        finish = False
                    if len(ret) == 0:
                        # 说明出错了
                        if self.stack:
                            # 开始回退，必须要回退到上一个有1个以上候选值的地方。
                            while True:
                                axis, num, last_set = self.stack.pop()
                                if last_set:
                                    cnt += 1
                                    self.guess((last_set, axis))
                                    return cnt, finish, min_set
                                else:
                                    self.free_fake_data(axis)
                        else:
                            raise
                        # break
                    elif len(ret) == 1:
                        cnt += 1
                        self.fill_fake_data((x, y), ret.pop(), ret)
                    else:
                        if (not min_set) or (min_set[0] and ret < min_set[0]):
                            min_set = ret, (x, y)
                        else:
                            continue
        return cnt, finish, min_set

    def guess(self, min_set):
        _min_set, (x, y) = min_set
        self.fill_fake_data((x, y), _min_set.pop(), _min_set)
        return True

    def handle(self):
        while True:
            cnt, finish, min_set = self.check()
            if finish:
                # print(cnt, finish, min_set)
                self.true_data = self.data
                break
            else:
                if cnt:
                    continue
                else:
                    # 猜的阶段
                    self.guess(min_set)

        pprint(self.true_data)


if __name__ == '__main__':
    # data0 = [
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0]
    # ]

    data = [
        [9, 7, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 0, 5, 6, 3, 0, 0, 0],
        [0, 0, 6, 0, 9, 0, 0, 0, 4],
        [0, 3, 8, 0, 0, 0, 0, 0, 7],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [4, 0, 0, 0, 0, 0, 6, 9, 0],
        [5, 0, 0, 0, 4, 0, 8, 0, 0],
        [0, 0, 0, 9, 1, 6, 0, 5, 0],
        [0, 0, 0, 0, 0, 0, 0, 2, 1]
    ]
    n = NumberSet()
    n.import_data(data)
    n.handle()
