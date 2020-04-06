# -*- coding: utf-8 -*-

import sys

import protocol

def main(mds_addr, mds_port, study_state):
    p = protocol.Protocol(mds_addr=mds_addr, mds_port=mds_port)
    p.launch()
    x = p.query1(study_state)
    p.finish()

    print("receive payload:")
    print("{}".format(x))

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
