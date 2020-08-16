# -*- coding: utf-8 -*-

# 从存储网关下载一个文件。

# mike
# 2019-12-20

import protocol

def get2(sgw_addr, sgw_port, filepath):
    p = protocol.Protocol(sgw_addr, sgw_port)
    p.launch()
    rc = p.getfile2(filepath)
    if rc:
        print("file {} successfully downloaded!".format(filepath))
    else:
        print("file {} download failed!".format(filepath))
    p.finish()

def main(sgw_addr, sgw_port, filepath):
    get2(sgw_addr, sgw_port, filepath)

if __name__ == '__main__':
    import sys
    try:
        nr_args = len(sys.argv)
        if nr_args == 4:
            sgw_addr = sys.argv[1]
            sgw_port = int(sys.argv[2])
            filepath = sys.argv[3]
            main(sgw_addr, sgw_port, filepath)
        else:
            print("usage: {} sgw_addr sgw_port filepath".format(sys.argv[0]))
            sys.exit(-1)
    except KeyboardInterrupt:
        sys.exit(0)
