# @Time    : 2020/8/20 11:03
# @Author  : DaguguJ
# @Email   : 1103098607@qq.com
# @File    : decoration.py

from w8.w8_20.timing import Sta


class Test(object):
    @staticmethod
    def test(a):
        print(a)


@Sta.timing_
def count(a, b, c=1, d=2):
    return (a+b*c)/d


var1, var2, var3, var4 = 1, 10, 11, 2


if __name__ == '__main__':

    count(var1, var2, c=var3)
    # count(var1, var2)
