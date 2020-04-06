# -*- coding: utf-8 -*-

# 从存储网关获取一个 studyid 的文件列表

# mike
# 2020-03-10

import pprint
import protocol

def get3(sgw_addr, sgw_port, studyid):
    p = protocol.Protocol(sgw_addr, sgw_port)
    p.launch()
    filestat = p.getfilelist1(studyid)
    p.finish()
    pprint.pprint(filestat)

if __name__ == '__main__':
    import sys
    try:
        nr_args = len(sys.argv)
        if nr_args == 4:
            sgw_addr = sys.argv[1]
            sgw_port = int(sys.argv[2])
            studyid = sys.argv[3]
            get3(sgw_addr, sgw_port, studyid)
        else:
            print("usage: {} sgw_addr sgw_port studyid".format(sys.argv[0]))
            sys.exit(-1)
    except KeyboardInterrupt:
        sys.exit(0)
