# -*- coding: utf-8 -*-

# 将一个特定的文件上传至存储网关。

# mike
# 2019-12-09

import protocol

def put1(sgw_addr, sgw_port, filepath):
    p = protocol.Protocol(sgw_addr, sgw_port)
    p.launch()
    p.putfile1(filepath)
    p.finish()

def main():
    import sys
    try:
        nr_args = len(sys.argv)
        if nr_args == 4:
            sgw_addr = sys.argv[1]
            sgw_port = int(sys.argv[2])
            filepath = sys.argv[3]
            put1(sgw_addr, sgw_port, filepath)
        else:
            print("usage: {} sgw_addr sgw_port filepath".format(sys.argv[0]))
            sys.exit(-1)
    except KeyboardInterrupt:
        sys.exit(0)

if __name__ == '__main__':
    main()
