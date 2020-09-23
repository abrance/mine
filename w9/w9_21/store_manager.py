
"""
使用说明： 服务于web应用 的数据存储，作为缓存来使用，
因为这个系统有明显地 时间-访问量 不平均（具体表现为，某一时间段）的关系，所以根据这一行为可以设计一套
系统进行高效率的保存和检索数据信息

需要考虑合并的时机
1.允许通过数据量大小进行合并
2.允许通过某一时间进行合并

需要抽象数据
运行任何形式的数据
"""


class MemTable(object):
    """
    内存模型基类。
    """
    def __init__(self):
        self.cache = dict()


class FrozenMemTable(MemTable):
    """
    不可变内存模型
    与磁盘文件的数据一致。属性：只读。
    """
    def __init__(self):
        super(FrozenMemTable, self).__init__()


class HotMemTable(MemTable):
    """
    可变内存模型
    如果需要更新数据，在这里进行更新。属性：只保存修改的日志。
    """
    def __init__(self):
        super(HotMemTable, self).__init__()
