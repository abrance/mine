# -*- coding: utf-8 -*-
#
# 自动化功能测试使用的配置文件
#
# mike
# 2020-03-10

import collections

# 存储网关的地址和端口
sgw_addr = "127.0.0.1"
sgw_port = 7788

# 以指定的顺序执行测试用例
how_to_test = "plan"

# 以下测试执行 3 轮。
# 第一轮执行：test1
# 第二轮执行：test2 test3
# 第三轮执行：test1 ~ "test{}".format(max_nr_test)
max_nr_test = 1000
plans = collections.OrderedDict(
    [
        ("plan1", ["test1"]),
        ("plan2", ["test2", "test3"]),
        ("plan3", ["test{}".format(i) for i in range(1, max_nr_test+1)])
    ]
)
