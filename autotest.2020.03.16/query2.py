# -*- coding: utf-8 -*-

# 单一检查列表查询接口的测试。

# mike
# 2019-12-13

import sys

import protocol

def main(mds_addr, mds_port, study_state):
    p = protocol.Protocol(mds_addr=mds_addr, mds_port=mds_port)
    p.launch()
    r, x = p.query2(study_state)
    p.finish()

    print("return code:", r)
    print("payload:")
    print(x)

if __name__ == '__main__':
    argc = len(sys.argv)
    if argc == 4:
        mds_addr = sys.argv[1]
        mds_port = int(sys.argv[2])
        study_state = int(sys.argv[3])
    else:
        print("usage: {} mds_addr mds_port study_state".format(sys.argv[0]))
        sys.exit(-1)

    try:
        main(mds_addr, mds_port, study_state)
    except KeyboardInterrupt:
        sys.exit(-1)
