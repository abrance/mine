import threading
import time
from collections import OrderedDict


class LRUCache(threading.Thread):
    """不能存储可变类型对象，不能并发访问set()"""
    def __init__(self, capacity, auto_pop=False):
        self.capacity = capacity
        self.cache = OrderedDict()
        self.auto_pop = auto_pop
        super(LRUCache, self).__init__()

    def get(self, key):
        if key in self.cache:
            value = self.cache.pop(key)
            self.cache[key] = value
        else:
            value = None
        return value

    def set(self, key, value):
        if key in self.cache:
            value = self.cache.pop(key)
            self.cache[key] = value
        else:
            if len(self.cache) >= self.capacity:
                self.cache.popitem(last=False)  # pop出第一个item
                self.cache[key] = value
            else:
                self.cache[key] = value

    def pop(self, key):
        if key in self.cache:
            self.cache.pop(key, -1)
        return True

    def add_job(self):
        while True:
            if self.cache:
                self.cache.popitem()
                time.sleep(15)
            else:
                time.sleep(60)

    def run(self) -> None:
        if self.auto_pop:
            self.add_job()
        else:
            pass


class LIRSCache(object):
    """
    提供接口，供使用者调用，可以设置不同的规则保存静态和动态缓存区
    """
    def __init__(self, *args, **kwargs):
        self._c1_size = kwargs.get('dynamic_cache_max_size', 1000)
        self._c2_size = kwargs.get('static_cache_max_size', 10)
        if not (isinstance(self._c1_size, int) and isinstance(self._c2_size, int)):
            raise Exception

        # 2020/9/20 两个lru缓存区，一个是静态缓存区，一个是动态缓存区
        self.c1 = LRUCache(self._c1_size)
        self.c2 = LRUCache(self._c2_size)

    def get_in_c1(self, key):
        return self.c1.get(key)

    def get_in_c2(self, key):
        return self.c2.get(key)

    def get(self, key):
        c2_v = self.get_in_c2(key)
        if c2_v:
            return c2_v
        else:
            c1_v = self.get_in_c1(key)
            return c1_v

    def set_c1(self, k, v):
        return self.c1.set(k, v)

    def set_c2(self, k, v):
        return self.c2.set(k, v)
