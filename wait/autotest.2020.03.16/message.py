# -*- coding: utf-8 -*-

import time
import struct
import socket

def ipv4_to_string(ipv4_int):
    """ipv4_int: 3232252436"""
    ipv4_bytes = ipv4_int.to_bytes(4, byteorder="big")
    ipv4_str = socket.inet_ntoa(ipv4_bytes)
    return ipv4_str

def ipv4_to_int(ipv4_str):
    """ipv4_str: 192.168.66.20"""
    ipv4_bytes = socket.inet_aton(ipv4_str)
    ipv4_tuple = struct.unpack("!I", ipv4_bytes)
    return ipv4_tuple[0]

HEADER_FORMAT   = "!I4BIIQQIIQQI4x"
HEADER_SIZE     = struct.calcsize(HEADER_FORMAT)
TASKINFO_FORMAT = "!HHIIIHH5IQ33s256sI"
TASKINFO_SIZE   = struct.calcsize(TASKINFO_FORMAT)

class Header:
    def __init__(self):
        self.total_size = 0
        self.major      = 1
        self.minor      = 0

        self.src_type   = 1 # client
        self.dst_type   = 2 # metadata
        self.src_id     = 20191130
        self.dst_id     = 0

        self.tranid     = 1
        self.sequence   = 1
        self.command    = 0
        self.ack_code   = 200

        self.total      = 0
        self.offset     = 0
        self.count      = 0

        self.format = HEADER_FORMAT
        self.size = HEADER_SIZE

    def pack(self):
        header_unpack = (
            self.total_size, self.major, self.minor,
            self.src_type, self.dst_type, self.src_id, self.dst_id,
            self.tranid, self.sequence,
            self.command, self.ack_code,
            self.total, self.offset, self.count
        )
        return struct.pack(self.format, *header_unpack)

    @staticmethod
    def unpack(blob):
        H = struct.unpack(HEADER_FORMAT, blob)
        h = Header()
        h.total_size = H[0]
        h.major      = H[1]
        h.minor      = H[2]
        h.src_type   = H[3]
        h.dst_type   = H[4]
        h.src_id     = H[5]
        h.dst_id     = H[6]
        h.tranid     = H[7]
        h.sequence   = H[8]
        h.command    = H[9]
        h.ack_code   = H[10]
        h.total      = H[11]
        h.offset     = H[12]
        h.count      = H[13]
        return h

class Taskinfo:
    def __init__(self):
        self.operation    = 1
        self.region_id    = 0
        self.site_id      = 0
        self.app_id       = 0
        self.timestamp    = int(time.time())
        self.sgw_port     = 0
        self.proxy_port   = 0
        self.sgw_ipv4     = 0
        self.proxy_ipv4   = 0
        self.sgw_id       = 0
        self.proxy_id     = 0
        self.pad_1        = 0
        self.file_len     = 0
        self.file_md5     = b""
        self.file_name    = b""
        self.metadata_len = 0

        self.format = TASKINFO_FORMAT
        self.size = TASKINFO_SIZE

    def pack(self):
        taskinfo_unpack = (
            self.operation,
            self.region_id, self.site_id, self.app_id, self.timestamp,
            self.sgw_port, self.proxy_port, self.sgw_ipv4, self.proxy_ipv4,
            self.sgw_id, self.proxy_id, self.pad_1,
            self.file_len, self.file_md5, self.file_name,
            self.metadata_len
        )
        return struct.pack(self.format, *taskinfo_unpack)

    @staticmethod
    def unpack(blob):
        return struct.unpack(TASKINFO_FORMAT, blob)


# 最多有两部分
class Message2:
    def __init__(self):
        self.header = Header()
        self.payload = b""

    def pack(self):
        payload_len = len(self.payload)
        if payload_len > 0:
            self.header.total_size = self.header.size + payload_len
            header_pack = self.header.pack()
            return header_pack + self.payload
        else:
            self.header.total_size = self.header.size
            header_pack = self.header.pack()
            return header_pack


# 最多三部分
class Message3:
    def __init__(self):
        self.header = Header()
        self.taskinfo = Taskinfo()
        self.payload = b""

    def pack(self):
        payload_len = len(self.payload)
        if payload_len > 0:
            self.header.total_size = self.header.size + self.taskinfo.size + payload_len
            self.taskinfo.metadata_len = payload_len
            header_pack = self.header.pack()
            taskinfo_pack = self.taskinfo.pack()
            return header_pack + taskinfo_pack + self.payload
        else:
            self.header.total_size = self.header.size + self.taskinfo.size
            self.taskinfo.metadata_len = 0
            header_pack = self.header.pack()
            taskinfo_pack = self.taskinfo.pack()
            return header_pack + taskinfo_pack
