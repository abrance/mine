import time
from queue import Queue
from threading import Thread


db_dir_id = []


def get_max_dir_id():
    return max(db_dir_id) if db_dir_id else 0


class DirIdQueue(Thread):
    """
    自动创建队列，拿到数据库最大的id，从而实现，既是自增id，又可以方便批量插入数据，但是能简单的获取到 id这一数据；假如，id需要马上用的情况，比如加入到缓存
    """
    def __init__(self):
        super(DirIdQueue, self).__init__()
        self.dir_id_queue = Queue(maxsize=-1)
        self.lock = False
        self.max_id = -1

    def get_lock(self):
        if self.lock:
            return False
        else:
            self.lock = True
            return True

    def free_lock(self):
        if self.lock:
            self.lock = False
        return True

    def put(self):
        if self.lock:
            return False
        else:
            self.get_lock()

            if self.max_id == -1:
                # 2020/11/5 如果还是初始值就去查数据库取max_id
                max_id = get_max_dir_id()
                if isinstance(max_id, int):
                    pass
                else:
                    return False

                for i in range(max_id+1, max_id+5001):
                    self.dir_id_queue.put(i)
                self.max_id = max_id+5000
                self.free_lock()

                return True
            else:

                size = self.dir_id_queue.qsize()
                # 2020/11/16 这里控制size 大小
                if size <= 5000:
                    max_id_in_q = self.max_id
                    new_max_id_in_q = max_id_in_q + 5001
                    # 2020/11/16 put in 5000 id
                    for i in range(max_id_in_q+1, new_max_id_in_q):
                        self.dir_id_queue.put(i)
                    self.max_id = new_max_id_in_q-1
                    self.free_lock()
                    return True
                else:
                    return True

    def run(self) -> None:
        while True:
            if self.dir_id_queue.qsize() <= 5000:
                self.put()
            else:
                time.sleep(0.5)


class IdConsumer(Thread):
    def __init__(self, que: Queue):
        self.queue = que
        self.last = None
        super(IdConsumer, self).__init__()

    def consume(self):
        qsize = self.queue.qsize()
        if qsize:
            dir_id = self.queue.get()
            if self.last is not None:
                if dir_id - self.last == 1:
                    pass
                else:
                    print('last: {} dir_id: {}'.format(self.last, dir_id))
                    print('error')
                    raise Exception
                pass

            self.last = dir_id
        else:
            time.sleep(1)
            print('consume qsize: {}'.format(qsize))

    def run(self) -> None:
        while True:
            self.consume()


if __name__ == '__main__':
    dq = DirIdQueue()
    dq.start()
    ic = IdConsumer(dq.dir_id_queue)
    ic.start()
