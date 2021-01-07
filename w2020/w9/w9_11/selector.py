from multiprocessing import Process, Queue


infinity_queue = Queue(maxsize=-1)


class BaseSelector(object):
    """
    选择基类
    """

    def __init__(self, handler=None):
        self.handler = handler
        if not self.handler:
            pass
        pass

    def select(self, items: iter):
        """
        可以选择很多元素，可以选择各种规则（甚至可以进行排序），如果内容过大，可以分部排序（分多次排序）
        :param items: 一个可迭代对象，（其实也可以不是），自行实现算法即可
        :return: 返回一个元素对象（也可以是多个元素）
        """
        pass


class BaseHandler(object):
    """
    处理基类
    """
    def __init__(self):
        pass

    def handle(self):
        pass

    def scheduler(self):
        pass


class MultiprocessHandler(Process, BaseHandler):
    """
    多进程处理基类
    """
    def __init__(self):
        super(MultiprocessHandler, self).__init__()
        pass

    def add_job(self):
        pass

    def handle(self):
        super(MultiprocessHandler, self).handle()

    def scheduler(self):
        super(MultiprocessHandler, self).scheduler()

    def run(self) -> None:
        pass
