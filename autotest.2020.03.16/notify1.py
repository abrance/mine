# -*- coding: utf-8 -*-

# 上传成功通知接口的测试。

# mike
# 2019-12-13

import sys

import protocol

finish_list = [
    {"agent_id": 1209, "study_id": "1.2.3.4.111", "nr_files": 200},
    {"agent_id": 1213, "study_id": "1.2.3.4.222", "nr_files": 100}
]

def main(mds_addr, mds_port):
    p = protocol.Protocol(mds_addr=mds_addr, mds_port=mds_port)
    p.launch()
    r = p.notify1(finish_list)
    p.finish()
    print("return code:", r)

if __name__ == '__main__':
    argc = len(sys.argv)
    if argc == 3:
        mds_addr = sys.argv[1]
        mds_port = int(sys.argv[2])
    else:
        print("usage: {} mds_addr mds_port".format(sys.argv[0]))
        sys.exit(-1)

    try:
        main(mds_addr, mds_port)
    except KeyboardInterrupt:
        sys.exit(-1)
