"""
类似 [('1', 1), ('2', 'j'), ('3', 1372)] (('1', 1), ('2', 'j'), ('3', 1372))这种可以直接转
"""

cc = [('1', 1), ('2', 'j'), ('3', 1372)]


def tuple_to_dict(_tuple):
    dc = dict(_tuple)
    return dc


if __name__ == '__main__':
    dd = tuple_to_dict(cc)
    print(dd)
