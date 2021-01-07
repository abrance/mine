
def statistic(s: str):
    # python 统计 字符串每个字符出现的频率
    dc = {}
    for _s in s:
        if _s not in dc.keys():
            dc[_s] = 1
        else:
            dc[_s] += 1
    return dc


if __name__ == '__main__':
    string = ' \n'
    a = statistic(string)
    print(a)
