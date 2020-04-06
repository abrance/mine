# -*- coding: utf-8 -*-

# <蓝网方案>mds处理客户端消息的时候出现过drop response message: no route to host

# 重现步骤：
#
# 1. 建立到 mds 的连接
# 2. 发送一个查询检查列表的请求
# 3. 发送之后马上关闭连接
#
# 此时，mds 日志应该会出现“drop responsed message”的日志，此后再次发送正常的请求，
# 也不会再收到响应了。

import time
import json
import struct
import socket

import config
import utils
import message

default_mds_addr = "192.168.66.21"
default_mds_port = 7788

def sendrq1(sock):
    """发送获取检查列表请求"""
    args_unpack = dict()
    args_unpack["timestamp_before"] = int(time.time())
    args_unpack["agent_id"] = 7777
    args_unpack["nr_study"] = 10
    args_unpack["study_state"] = 0
    args_unpack["nr_files"] = 0
    args_unpack["study_id"] = "useless_study_id"

    args_pack = json.dumps(args_unpack).encode("utf-8")
    args_size = len(args_pack)
    head_size = config.Constant.HEAD_LENGTH

    # header
    h = message.Header()
    h.command = config.Constant.CLIENT_QUERY_STUDY_LIST
    h.total_size = head_size + args_size
    header_pack = h.pack()

    # entire packet
    pkt = header_pack + args_pack
    
    # send
    sock.sendall(pkt)

def recvrs1(sock):
    """接收获取检查列表响应"""
    sock.settimeout(5)
    block = sock.recv(config.Constant.HEAD_LENGTH)

def main(mds_addr, mds_port):
    n = 0
    while True:
        sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock1.connect((mds_addr, mds_port))
        sendrq1(sock1)
        # 注意，这里故意没有接收响应就关闭连接
        if n > 0:
            try:
                recvrs1(sock1)
                sock1.close()
            except socket.timeout:
                print("bug reproduce!")
                break
        else:
            sock1.close()

        sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock2.connect((mds_addr, mds_port))
        sendrq1(sock2)
        try:
            recvrs1(sock2)
            sock2.close()
        except socket.timeout as e:
            print("bug reproduce! please check mds log ...")
            break
        
        n = n + 1

if __name__ == '__main__':
    import sys
    try:
        nr_args = len(sys.argv)
        if nr_args == 1:
            mds_addr = default_mds_addr
            mds_port = default_mds_port
        elif nr_args == 2:
            mds_addr = sys.argv[1]
            mds_port = default_mds_port
        elif nr_args == 3:
            mds_addr = sys.argv[1]
            mds_port = int(sys.argv[2])
        else:
            print("usage: {} [mds_addr] [mds_port]".format(sys.argv[0]))
            print("default: mds_addr: {}, mds_port: {}".format(
                default_mds_addr, default_mds_port
            ))
            sys.exit(-1)
        main(mds_addr, mds_port)
    except KeyboardInterrupt:
        import sys
        sys.exit(0)
