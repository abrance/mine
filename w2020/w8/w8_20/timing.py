# @Time    : 2020/8/20 11:30
# @Author  : DaguguJ
# @Email   : 1103098607@qq.com
# @File    : timing.py
import inspect
import time


class Sta(object):
    @staticmethod
    def timing_(func):
        # 2020/4/10 计时装饰器
        def wrapper(*args, **kwargs):
            start_time = time.time()
            ret = func(*args, **kwargs)
            end_time = time.time()
            cost_time = end_time-start_time
            print("{}消耗时间为{}".format(func.__name__, cost_time))
            _len = len(args) + len(kwargs.keys())
            print(_len)

            print(inspect.currentframe().f_back.f_locals.keys())

            # 2020/8/20 不能获取到这个函数中传入的变量名、值
            ls = list(inspect.currentframe().f_back.f_locals.keys())[-_len:]
            print(ls)

            for i in ls:
                print('{}: {}'.format(i, inspect.currentframe().f_back.f_locals[i]))
            return ret
        return wrapper
