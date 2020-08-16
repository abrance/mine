# -*- coding: utf-8 -*-

# <蓝网方案>文件上传：客户端在处理文件上传的同时，请求文件下载，出现sgw ack code is 0

# 禅道记录的问题 #260 重现步骤：
#
# 1. 发送 405=64(header)+241(taskinfo) 字节到 sgw
# 2. 响应的消息也是 405 字节，但是只接收并处理 64 字节
# 3. 继续发送 64 字节到 sgw
# 4. 接收 64 响应
# 5. 问题出现

import utils
import message

default_sgw_addr = "192.168.66.31"
default_sgw_port = 7788

file_content = b"reproduce bug260"

# 发送“开始上传”请求，消息格式为：
#
# header(64) + taskinfo(341)
def sendrq1(sock):
    """发送开始上传请求，消息格式为 header(64) + taskinfo(341)"""
    # taskinfo
    t = message.Taskinfo()
    import hashlib
    m = hashlib.md5()
    m.update(file_content)
    t.file_md5 = m.hexdigest().encode("utf-8")
    t.file_name = b"reproduce-bug260"
    t.sgw_ipv4 = message.ipv4_to_int(sgw_addr)
    T = t.pack()

    # header
    h = message.Header()
    h.command = 0x00020001
    # import random
    # h.total_size = 64 + len(T) + random.randint(1, 10)
    h.total_size = 64 + len(T)
    h.total = len(file_content)
    h.offset = 0
    h.count = 0
    H = h.pack()
    
    # packet = header + taskinfo
    # pkt = H + T + H + T
    pkt = H + T

    sock.sendall(pkt)

def recvrs1(sock):
    """接收“开始请求“的响应，消息格式为：header(64)+taskinfo(341)"""
    H = sock.recv(64)
    if len(H) == 64:
        # h = message.Header.unpack(H)
        pass
    else:
        print("recv header failed: {} want, {} recv".format(
            64, len(H)
        ))
    # 接收到此结束，故意不接收剩下的字节

def sendrq2(sock):
    """发送”上传文件内容“请求，消息格式：header(64)+data(?)"""
    # header
    h = message.Header()
    h.command = 0x00020003
    h.total_size = 64 + len(file_content)
    h.total = len(file_content)
    h.offset = 0
    h.count = len(file_content)
    H = h.pack()
    
    # packet
    pkt = H + file_content

    # send
    sock.sendall(pkt)

def recvrs2(sock):
    """接收响应"""
    H = sock.recv(64)
    if len(H) == 64:
        h = message.Header.unpack(H)
        if h.ack_code == 0:
            print("bug reproduce! ack code {}".format(h.ack_code))
        else:
            pass
    else:
        print("recv header failed: {} want, {} recv".format(
            64, len(H)
        ))

def sendrq3(sock):
    pass

def recvrs3(sock):
    pass

def main(sgw_addr, sgw_port):
    sock = utils.create_client_socket(sgw_addr, sgw_port)
    sendrq1(sock)
    recvrs1(sock)
    sendrq2(sock)
    recvrs2(sock)
    sock.close()

if __name__ == '__main__':
    import sys
    try:
        nr_args = len(sys.argv)
        if nr_args == 1:
            sgw_addr = default_sgw_addr
            sgw_port = default_sgw_port
        elif nr_args == 2:
            sgw_addr = sys.argv[1]
            sgw_port = default_sgw_port
        elif nr_args == 3:
            sgw_addr = sys.argv[1]
            sgw_port = int(sys.argv[2])
        else:
            print("usage: {} [sgw_addr] [sgw_port]".format(sys.argv[0]))
            print("default: sgw_addr: {}, sgw_port: {}".format(
                default_sgw_addr, default_sgw_port
            ))
            sys.exit(-1)
        main(sgw_addr, sgw_port)
    except KeyboardInterrupt:
        import sys
        sys.exit(0)
