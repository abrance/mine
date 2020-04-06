# -*- coding: utf-8 -*-

import struct
import socket

from log import logger

def attempt_recvall(conn, length):
    """从阻塞的 conn 中接收指定长度 length 的字节

    如果发生超时、对端关闭连接、系统错误，那么 attempt_recvall 的返回值可能是
    (0~length, data)；如果没有发生以上的情况，将会返回 (len(data), data)。

    """

    blocks = []

    recvtotal = 0
    recvleft = length

    notimeout = True
    noerror = True
    noeof = True

    while ((recvtotal != length) and
           (notimeout == True) and
           (noerror == True) and
           (noeof == True)):
        try:
            block = conn.recv(recvleft)
        except socket.timeout as e:
            logger.error(
                "socket.recv timeout: {0}, sock={1}, want={2}, recv={3}".format(
                    e, id(conn), length, recvtotal))
            notimeout = False
        except OSError as e:
            logger.error(
                "socket.recv failed: {0}, sock={1}, want={2}, recv={3}".format(
                    e, id(conn), length, recvtotal))
            noerror = False
        else:
            recvlen = len(block)
            if recvlen > 0:
                recvtotal += recvlen
                recvleft -= recvlen
                blocks.append(block)
            else:
                logger.warning(
                    "socket.recv uncompleted: sock={0}, want={1}, recvlen={2}".format(
                        id(conn), length, recvlen))
                noeof = False

    return (recvtotal, b''.join(blocks))

def get_msg(sock, header_length, header_format):
    """从 sock 中获取一个完整的消息

    分为两次获取消息，第一次收取消息头部；在消息头部中获取消息余下的长度，在第二
    次收取余下的消息内容。

    """
    recvlen, header = attempt_recvall(sock, header_length)
    if recvlen == header_length:
        try:
            header_unpack = struct.unpack(header_format, header)
            header_unpack_len = struct.calcsize(header_format)
        except struct.error as e:
            logger.error("unpack header failed: {0}".format(e))
            return (0, None, 0, None)
        else:
            total_size = header_unpack[0]
            body_size = total_size - header_length
            if body_size > 0:
                recvlen, body = attempt_recvall(sock, body_size)
                if recvlen == body_size:
                    return (header_unpack_len, header_unpack, body_size, body)
                else:
                    logger.error("recv body failed: want={0}, recv={1}".format(
                        body_size, recvlen))
                    return (header_unpack_len, header_unpack, body_size, None)
            else:
                return (header_unpack_len, header_unpack, 0, None)
    else:
        logger.error("recv header failed: want={0}, recv={1}".format(
            header_length, recvlen))
        return (0, None, 0, None)

def create_server_socket(listen_ip, listen_port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except OSError as e:
        logger.error("created tcp socket failed: {0}".format(e))
        return None
    else:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setblocking(False)
        try:
            sock.bind((listen_ip, listen_port))
        except OSError as e:
            logger.error("bind {0}:{1} failed: {2}".format(listen_ip, listen_port, e))
            sock.close()
            return None
        else:
            try:
                sock.listen(100)
            except OSError as e:
                logger.error("listen failed: {0}".format(e))
                sock.close()
                return None
            else:
                logger.info("listening on {0}:{1}".format(listen_ip, listen_port))
                return sock

def create_client_socket(server_ip, server_port):
    addr = (server_ip, server_port)
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as e:
        logger.error("created socket failed: {0}".format(e))
        return None
    else:
        try:
            sock.settimeout(3)
            sock.connect(addr)
            sock.setblocking(True)
        except socket.error as e:
            logger.error("connect to {0} failed: {1}".format(addr, e))
            sock.close()
            return None
        except socket.timeout as e:
            logger.error('connect to {0} timeout: {1}'.format(addr, e))
            sock.close()
            return None
        else:
            logger.info('connect to {0} success'.format(addr))
            return sock

def calcmd5(filepath):
    import hashlib
    m = hashlib.md5()
    with open(filepath, "rb") as f:
        while True:
            content = f.read(4096)
            if content:
                m.update(content)
            else:
                break
    return m.hexdigest()

def removefile(filename):
    import os
    if os.path.exists(filename):
        os.remove(filename)
    else:
        pass

def xor(filename, offset):
    with open(filename, "rb+") as f:
        f.seek(offset)
        x = f.read(1)
        a = int.from_bytes(x, "little")
        a = a ^ 1
        x = a.to_bytes(1, "little")
        f.seek(offset)
        f.write(x)

def removedir(dirname):
    import os
    if os.path.isdir(dirname):
        import shutil
        shutil.rmtree(dirname)
    else:
        pass
