import threading
import time
from collections import OrderedDict


"""
LRUCache 实现了一个可设置长度的 缓存空间，实现了lru算法
实现了 过一段时间就开始pop最后一个数据
"""


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
