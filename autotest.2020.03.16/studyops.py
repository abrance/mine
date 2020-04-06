# -*- coding: utf-8 -*-
"""
@file: studyid.py
@desc:
@author: Jaden Wu
@time: 2019/10/15 9:32

2020-03-12: Modified by mike
"""
import os
from ctypes import c_int32, Structure

crc32_table = []
s_hash_count = 4096


def get_crc32(instr, length):
    # 生成crc32的查询表
    if not crc32_table:
        # print('生成crc32查询表')
        for i in range(256):
            crc = i
            for j in range(8):
                if crc & 1:
                    crc = (crc >> 1) ^ 0xEDB88320
                else:
                    crc >>= 1
            crc32_table.append(crc)

    # 开始计算crc32校验值
    crc = 0xffffffff
    for i in range(length):
        crc = (crc >> 8) ^ crc32_table[(crc & 0xff) ^ ord(instr[i])]
    crc ^= 0xffffffff
    return crc


def get_hash_key(uid_str):
    crc = get_crc32(uid_str, len(uid_str))
    result = crc % s_hash_count
    return result


def get_first_two_level(uid):
    key = get_hash_key(uid)
    return key // 64, key % 64


class Point(Structure):
    _fields_ = ("x", c_int32), ("y", c_int32)


def get_last_two_level(study_id_str):
    # 素数
    multiplier1 = 31
    multiplier2 = 37
    divider1 = 101
    divider2 = 103

    study_id_str_length = len(study_id_str)
    p = Point()

    for i in range(study_id_str_length):
        p.x = p.x * multiplier1 + ord(study_id_str[i])
    p.x %= divider1
    if p.x < 0:
        p.x += divider1

    for i in range(study_id_str_length):
        p.y = p.y * multiplier2 + ord(study_id_str[i])
    p.y %= divider2
    if p.y < 0:
        p.y += divider2
    return p.x, p.y


def calcpath(study_id_str):
    d1, d2 = get_first_two_level(study_id_str)
    d3, d4 = get_last_two_level(study_id_str)
    return os.sep.join((str(d1), str(d2), str(d3), str(d4)))


if __name__ == '__main__':
    import sys
    if len(sys.argv) == 1:
        print(study_id_to_path('1.2.826.0.1.3680043.2.461.9701983.3645589902'))  # \4\60\90\100\
    elif len(sys.argv) == 2:
        print(study_id_to_path(sys.argv[1]))
    else:
        pass
