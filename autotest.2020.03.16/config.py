# -*- coding: utf-8 -*-

import os
import configparser
import struct

MAJOR_VERSION = 1
MINOR_VERSION = 0
CLIENT_TYPE   = int(0x01)
METADATA_TYPE = int(0x02)
SGW_TYPE      = int(0x03)

# client <-> mds
# client 与 mds 交互的消息包类型
MDS_UPLOAD_REQ         = int(0x00000001)
MDS_UPLOAD_RSP         = int(0x00000002)
MDS_UPLOAD_RET         = int(0x00000003)
MDS_QUERY_FILENUM_REQ  = int(0x00000004)
MDS_QUERY_FILENUM_RSP  = int(0x00000005)
MDS_QUERY_FILEMETA_REQ = int(0x00000006)
MDS_QUERY_FILEMETA_RSP = int(0x00000007)
MDS_DELETE_REQ         = int(0x0000000C)
MDS_DELETE_RSP         = int(0x0000000D)

# client <-> sgw
# client 和 sgw 交互的消息包类型
SGW_UPLOAD_START_REQ   = int(0x00020001)
SGW_UPLOAD_START_RSP   = int(0x00020002)
SGW_UPLOAD_DATA_REQ    = int(0x00020003)
SGW_UPLOAD_DATA_RSP    = int(0x00020004)
SGW_UPLOAD_END_REQ     = int(0x00020005)
SGW_UPLOAD_END_RSP     = int(0x00020006)
SGW_DOWNLOAD_START_REQ = int(0x00020007)
SGW_DOWNLOAD_START_RSP = int(0x00020008)
SGW_DOWNLOAD_DATA_REQ  = int(0x00020009)
SGW_DOWNLOAD_DATA_RSP  = int(0x0002000A)
SGW_DOWNLOAD_END_REQ   = int(0x0002000B)
SGW_DOWNLOAD_END_RSP   = int(0x0002000C)

# 数据迁移相关
MIGRATION_SGW_RECORD       = int(0x60000001) # sgw 迁移记录请求写入 sgw -> old_mds
MIGRATION_SGW_RECORD_RESP  = int(0x60000002)
MIGRATION_META_RECORD      = int(0x60000003) # meta 迁移记录传输请求 old_mds -> new_mds
MIGRATION_META_RECORD_RESP = int(0x60000004)

# client与metadata server通信 响应码
ACK_SUCCESS                  = 200
ACK_FAILED                   = 404
ACK_CLIENT_UPLOAD            = 200
ACK_CLIENT_UPLOAD_FAILED     = 404
ACK_CLIENT_QUERY_NUM         = 200
ACK_CLIENT_QUERY_NUM_FAILED  = 404
ACK_CLIENT_QUERY_DATA        = 200
ACK_CLIENT_QUERY_DATA_FAILED = 404
ACK_CLIENT_DEL_SUCCESS       = 200
ACK_CLIENT_DEL_FAILED        = 404


class Constant:
    MAJOR_VERSION = 1
    MINOR_VERSION = 0
    CLIENT_TYPE = int(0x01)
    METADATA_TYPE = int(0x02)
    SGW_TYPE = int(0x03)
    STATUS_TYPE = int(0x04)
    CONFIG_TYPE = int(0x05)

    FMT_COMMON_HEAD = '!I4BIIQQIIQQI4x'
    HEAD_LENGTH = struct.calcsize(FMT_COMMON_HEAD)
    FMT_TASKINFO_FIXED = '!HHIIIHH5IQ33s256sI'
    TASKINFO_LENGTH = struct.calcsize(FMT_TASKINFO_FIXED)

    # client与metadata server通信 命令字
    CLIENT_UPLOAD = int(0x00000001)
    CLIENT_UPLOAD_RESP = int(0x00000002)
    CLIENT_UPLOAD_SUCCESS = int(0x00000003)
    CLIENT_QUERY_NUM = int(0x00000004)
    CLIENT_QUERY_NUM_RESP = int(0x00000005)
    CLIENT_QUERY_DATA = int(0x00000006)
    CLIENT_QUERY_DATA_RESP = int(0x00000007)
    CLIENT_DEL = int(0x0000000C)
    CLIENT_DEL_RESP = int(0x0000000D)
    CLIENT_PUSH_DIR_LIST = int(0x00000012)
    CLIENT_PUSH_DIR_LIST_RESP = int(0x00000013)
    CLIENT_QUERY_STUDY_LIST = int(0x00000010)
    CLIENT_QUERY_STUDY_LIST_RESP = int(0x00000011)
    CLIENT_MOVE_BACK_NOTIFY = int(0x00000014)
    CLIENT_MOVE_BACK_NOTIFY_RESP = int(0x00000015)

    # 数据迁移相关
    MIGRATION_SGW_RECORD = int(0x60000001)  # sgw 迁移记录请求写入 sgw -> old_mds
    MIGRATION_SGW_RECORD_RESP = int(0x60000002)
    MIGRATION_META_RECORD = int(0x60000003)  # meta 迁移记录传输请求 old_mds -> new_mds
    MIGRATION_META_RECORD_RESP = int(0x60000004)

    # client与metadata server通信 响应码
    ACK_SUCCESS = 200
    ACK_FAILED = 404
    ACK_CLIENT_UPLOAD = 200
    ACK_CLIENT_UPLOAD_FAILED = 404
    ACK_CLIENT_QUERY_NUM = 200
    ACK_CLIENT_QUERY_NUM_FAILED = 404
    ACK_CLIENT_QUERY_DATA = 200
    ACK_CLIENT_QUERY_DATA_FAILED = 404
    ACK_CLIENT_DEL_SUCCESS = 200
    ACK_CLIENT_DEL_FAILED = 404
    ACK_CLIENT_DIR_PUSH_SUCCESS = 200
    ACK_CLIENT_DIR_PUSH_FAILED = 404

command_str = {
    Constant.CLIENT_UPLOAD: "CLIENT_UPLOAD",
    Constant.CLIENT_UPLOAD_RESP: "CLIENT_UPLOAD_RESP",
    Constant.CLIENT_UPLOAD_SUCCESS: "CLIENT_UPLOAD_SUCCESS",
    Constant.CLIENT_QUERY_NUM: "CLIENT_QUERY_NUM",
    Constant.CLIENT_QUERY_NUM_RESP: "CLIENT_QUERY_NUM_RESP",
    Constant.CLIENT_QUERY_DATA: "CLIENT_QUERY_DATA",
    Constant.CLIENT_QUERY_DATA_RESP: "CLIENT_QUERY_DATA_RESP",
    Constant.CLIENT_DEL: "CLIENT_DEL",
    Constant.CLIENT_DEL_RESP: "CLIENT_DEL_RESP",
    Constant.MIGRATION_SGW_RECORD: "MIGRATION_SGW_RECORD",
    Constant.MIGRATION_SGW_RECORD_RESP: "MIGRATION_SGW_RECORD_RESP",
    Constant.MIGRATION_META_RECORD: "MIGRATION_META_RECORD",
    Constant.MIGRATION_META_RECORD_RESP: "MIGRATION_META_RECORD_RESP",
}

class Config:
    def __init__(self, meta_path=None):
        self.c = configparser.ConfigParser()
        if meta_path is None:
            basedir = os.path.abspath(os.path.dirname(__file__))
            meta_path = os.path.join(basedir, 'meta.ini')
        self.c.read(meta_path, encoding='utf-8')
        self.region_id    = self.c.getint('local_config', 'region_id')
        # self.site_id      = int(self.c.get('local_config', 'site_id'))
        # self.app_id       = int(self.c.get('local_config', 'app_id'))
        # self.system_id    = int(self.c.get('local_config', 'system_id'))
        self.src_id       = int(self.c.get('local_config', 'src_id'), 16)
        # self.dst_mds_id   = int(self.c.get('local_config', 'dst_mds_id'), 16)
        # self.dst_mds_ip   = self.c.get('local_config', 'dst_mds_ip')
        # self.dst_mds_port = int(self.c.get('local_config', 'dst_mds_port'))
        # self.dst_sgw_id   = int(self.c.get('local_config', 'dst_sgw_id'), 16)
        # self.dst_sgw_ip   = self.c.get('local_config', 'dst_sgw_ip')
        # self.dst_sgw_port = self.c.get('local_config', 'dst_sgw_port')

        self.db = self.c.get('mysql_db1', 'db')
        self.host = self.c.get('mysql_db1', 'host')
        self.user = self.c.get('mysql_db1', 'user')
        self.password = self.c.get('mysql_db1', 'password')

        self.mds_port = self.c.getint('local_config', 'mds_port')

        self.upload_path = self.c.get('auto_test_config', 'upload_path')
        self.download_path = self.c.get('auto_test_config', 'download_path')
        self.sgw_host = self.c.get('auto_test_config', 'sgw_host')
        self.sgw_port = self.c.getint('auto_test_config', 'sgw_port')

        self.site_id = self.c.getint('auto_test_config', 'site_id')
        self.study_upload_conf = self.c.get('auto_test_config', 'study_upload_conf')
        self.study_download_conf = self.c.get('auto_test_config', 'study_download_conf')
        self.upload_nums = self.c.getint('auto_test_config', 'upload_nums')


config_info = Config()

