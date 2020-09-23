
"""
https://cloud.tencent.com/developer/news/340271

LSM 模型
log structure merge tree
对数据的修改增量保持在内存中，达到制定的大小限制后将修改操作批量写入磁盘，读趋势需要合并磁盘中的历史数据和内存中最近的修改操作。
LSM树的优势在于有效规避了磁盘随即写入问题，但读取时可能需要访问较多的磁盘文件。

适用场景： 写密集、少量查询的场景。
使用说明： 服务于web应用 的数据存储，作为缓存来使用，
因为这个系统有明显地 时间-访问量 不平均（具体表现为，某一时间段）的关系，所以根据这一行为可以设计一套
系统进行高效率的保存和检索数据信息
结构：
    LSM-tree 被分成三种文件，第一种是内存中的两个 memtable，一个是正常的接收写入请求的 memtable，一个是不可修改的immutable memtable
    另外一部分是磁盘上的 SStable （Sorted String Table），有序字符串表，这个有序的字符串就是数据的 key。SStable 一共有七层（L0 到 L6）。下一层的总大小限制是上一层的 10 倍。

写入流程：
首先将写入操作加到写前日志中，接下来把数据写到 memtable中，当 memtable 满了，就将这个 memtable 切换为不可更改的 immutable memtable，
并新开一个 memtable 接收新的写入请求。而这个 immutable memtable 就可以刷磁盘了。这里刷磁盘是直接刷成 L0 层的 SSTable 文件，并不直接跟 L0 层的文件合并。

注意：

需要考虑合并的时机
1.允许通过数据量大小进行合并
2.允许通过某一时间进行合并

需要抽象数据
运行任何形式的数据
"""
from threading import Thread


class MemTable(object):
    """
    内存模型基类。
    """
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = dict()

    def get(self, key):
        if key in self.cache:
            return self.cache.get(key)


class FrozenMemTable(MemTable):
    """
    不可变内存模型
    与磁盘文件的数据一致。属性：只读。 其实里面可以有很多层，是一层一层合并的 Compaction（合并）
    写入过程基本只用到了内存结构，Compaction 可以后台异步完成，不阻塞写入
    """
    def __init__(self):
        super(FrozenMemTable, self).__init__(10000)


class HotMemTable(MemTable):
    """
    可变内存模型
    如果需要更新数据，在这里进行更新。属性：只保存修改的日志。
    """
    def __init__(self):
        super(HotMemTable, self).__init__(1000)


class Compaction(Thread):
    """
    合并 行为类，实例一个合并行为，因为存在 内存->内存 内存->文件 文件->文件
    而且这个任务需要异步进行
    """
    def __init__(self):
        super(Compaction, self).__init__()
        pass

    def add_job(self):
        pass

    def run(self) -> None:
        self.add_job()
