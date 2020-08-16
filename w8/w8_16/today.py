"""
:DaguguJ write something everyday  2020/8/16
:param    None
:return    None
"""


def sort(ls):
    if len(ls) <= 1:
        return ls
    else:
        base = len(ls)//2
        ls1 = qs(ls, base)
        return ls1


def qs(ls: list, b):
    l1 = []
    l2 = []
    if len(ls) == 2:
        if ls[0] > ls[1]:
            ls.reverse()
            return ls
        else:
            return ls
    ls.remove(b)
    for i in ls:
        if i < ls[b]:
            l1.append(i)
        else:
            l2.append(i)
    _l = sort(l1) + [b] + sort(l2)
    return _l


if __name__ == '__main__':
    _ls = sort([1, 12, 3, 4, 2, 1, 5])
    print(_ls)
