
def merge_sort(ls: list):
    # 2020/9/19 二路归并排序
    length = len(ls)
    if length <= 1:
        return ls

    idx = length // 2
    piece1 = ls[:idx]
    piece2 = ls[idx:]

    piece1 = merge_sort(piece1)
    piece2 = merge_sort(piece2)
    sorted_ls = []
    # 2020/9/19 合并的算法
    while len(piece1) != 0 and len(piece2) != 0:
        if piece1[0] <= piece2[0]:
            sorted_ls.append(piece1[0])
            piece1 = piece1[1:]
        else:
            sorted_ls.append(piece2[0])
            piece2 = piece2[1:]

    if len(piece1) > 0:
        sorted_ls += piece1
    elif len(piece2) > 0:
        sorted_ls += piece2
    else:
        raise Exception

    return sorted_ls


l1 = [1, -1, 31, 23, 9, 4, 2, 3]


def main():
    l2 = merge_sort(l1)
    print(l2)
    l3 = sorted(l1)
    assert l2 == l3


if __name__ == '__main__':
    main()
