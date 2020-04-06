# -*- coding: utf-8 -*-

# 从存储网关下载一个文件，使用偏移下载的接口实现。
#
# mike
# 2020-03-11

import protocol

def get4(sgw_addr, sgw_port, filepath):
    p = protocol.Protocol(sgw_addr, sgw_port)
    p.launch()
    rc = p.getfile3(filepath)
    p.finish()
    return rc

if __name__ == '__main__':
    import sys
    try:
        nr_args = len(sys.argv)
        if nr_args == 4:
            sgw_addr = sys.argv[1]
            sgw_port = int(sys.argv[2])
            filepath = sys.argv[3]
            rc = get4(sgw_addr, sgw_port, filepath)
            sys.exit(rc)
        else:
            print("usage: {} sgw_addr sgw_port filepath".format(sys.argv[0]))
            sys.exit(-1)
    except KeyboardInterrupt:
        sys.exit(0)
