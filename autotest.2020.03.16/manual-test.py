# -*- coding: utf-8 -*-

# 接收用户的输入，运行特定的测试

import struct
import json
import time
import collections

import config
import utils
import pymysql
import time
import random
import os
import queue
import glob2
import hashlib
import io
import socket
import datetime

from config import config_info
from ctypes import *
from gen_path_by_study_id import study_id_to_path
from itertools import chain
from functools import reduce
from multiprocessing import Process

class Header:
    def __init__(self):
        self.total_size = 0
        self.major = config.Constant.MAJOR_VERSION
        self.minor = config.Constant.MINOR_VERSION
        self.src_type = config.Constant.CLIENT_TYPE
        self.dst_type = config.Constant.METADATA_TYPE
        self.src_id = config_info.src_id
        self.dst_id = 0x80000002
        self.tranid = 1
        self.sequence = 1
        self.command = config.Constant.CLIENT_UPLOAD
        self.ack_code = 200
        self.total = 1
        self.offset = 0
        self.count = 1

    def pack(self):
        header_unpack = (
            self.total_size, self.major, self.minor,
            self.src_type, self.dst_type, self.src_id, self.dst_id,
            self.tranid, self.sequence,
            self.command, self.ack_code,
            self.total, self.offset, self.count
        )
        return struct.pack(config.Constant.FMT_COMMON_HEAD, *header_unpack)

class MsgHeaders(BigEndianStructure):
    _pack_ = 1
    _fields_ = [('msg_length', c_uint32),
                ('major', c_uint8),
                ('minor', c_uint8),

                ('src_type', c_uint8),
                ('dst_type', c_uint8),
                ('src_id', c_uint32),
                ('dst_id', c_uint32),

                ('trans_id', c_uint64),
                ('sequence', c_uint64),

                ('command', c_uint32),
                ('ack_code', c_uint32),

                ('total', c_uint64),
                ('offset', c_uint64),
                ('count', c_uint32),

                ('padding', c_uint8 * 4),

                ('data', c_uint8 * 0)
                ]


class TaskInfo(BigEndianStructure):
    _pack_ = 1
    _fields_ = [('operation', c_uint16),
                ('region_id', c_uint16),
                ('site_id', c_uint32),
                ('app_id', c_uint32),
                ('timestamp', c_uint32),

                ('sgw_port', c_uint16),
                ('proxy_port', c_uint16),
                ('sgw_ip', c_uint32),
                ('proxy_ip', c_uint32),
                ('sgw_id', c_uint32),
                ('proxy_id', c_uint32),
                ('padding', c_uint32),

                ('file_len', c_uint64),
                ('file_md5', c_char * (32 + 1)),
                ('file_name', c_char * (255 + 1)),
                ('metadata_len', c_uint32),
                ('metadata', c_char * 0)
                ]


class HandleCommon(object):
    def __init__(self, site_id):
        self.msg_headers = MsgHeaders()
        self.msg_headers_len = sizeof(MsgHeaders)
        self.task_info = TaskInfo()
        self.msg_headers_len = sizeof(self.msg_headers)
        self.task_info_len = sizeof(self.task_info)

        self.msg_headers.major = 1
        self.msg_headers.minor = 1
        self.msg_headers.src_type = 1
        self.msg_headers.src_id = site_id

    def pack_data(self, body=None, task_info_extend=None):
        if body is None:
            body_len = self.task_info_len
            msg_body = string_at(addressof(self.task_info), self.task_info_len)
        else:
            body_len = len(body)
            msg_body = body
        if task_info_extend:
            body_len = self.task_info_len + len(task_info_extend)
            msg_body += task_info_extend.encode()
        self.msg_headers.msg_length = self.msg_headers_len + body_len
        msg_headers = string_at(addressof(self.msg_headers), self.msg_headers_len)  # type: bytes
        msg = msg_headers + msg_body
        return msg


class Body:
    def __init__(self):
        self.operation = 1
        self.region_id = 2018
        self.site_id = 11
        self.app_id = 12
        self.timestamp = int(time.time())
        self.sgw_port = 0
        self.proxy_port = 0
        self.sgw_ip = 0
        self.proxy_ip = 0
        self.sgw_id = 0
        self.proxy_id = 0
        self.pad_1 = 0
        self.file_len = 0
        self.file_md5 = b"unused-md5"
        self.file_name = b"unused-filename"
        self.metadata_len = 0

    def pack(self):
        body_unpack = (
            self.operation, self.region_id, self.site_id, self.app_id, self.timestamp,
            self.sgw_port, self.proxy_port, self.sgw_ip, self.proxy_ip,
            self.sgw_id, self.proxy_id, self.pad_1,
            self.file_len, self.file_md5, self.file_name, self.metadata_len
        )
        return struct.pack(config.Constant.FMT_TASKINFO_FIXED, *body_unpack)


class Upload(object):
    def __init__(self, file_path):
        self.types = ['dcm', 'ini', 'jpg', 'lwd', 'html']
        self.work_queue = queue.Queue()
        self.MD5_BLOCK_SIZE = 4 * 1024 * 1024
        self.sgw_sock = None

        self.msg_headers = MsgHeaders()
        self.msg_headers_len = sizeof(self.msg_headers)
        self.task_info = TaskInfo()
        self.task_info_len = sizeof(self.task_info)
        self.task_info_extend = ''

        self.file_path = file_path
        parent_path, self.file_name = os.path.split(self.file_path)
        self.msg_headers.major = 1
        self.msg_headers.minor = 1
        self.msg_headers.src_type = 1
        self.msg_headers.src_id = config_info.site_id

        self.task_info.site_id = config_info.site_id

        self.upload_trans_id = 0x0

    @staticmethod
    def cal_md5(file_path):
        with open(file_path, 'rb') as fr:
            file_md5_obj = hashlib.md5()
            while True:
                block = fr.read(4 * 1024 * 1024)
                if not block:
                    break
                file_md5_obj.update(block)
            file_md5 = file_md5_obj.hexdigest()
            return file_md5

    def queue_create(self):
        target_file_list = []
        result = list(map(lambda t: glob2.glob(os.path.join(self.file_path, u'**/*.%s' % t)), self.types))
        target_file_list.extend(list(reduce(lambda arg1, arg2: arg1 + arg2, result)))
        # target_file_list.extend(chain(list(map(lambda t: glob2.iglob(os.path.join(study_path, u'**/*.%s' % t)),
        #                                     self.types))))

        # print("target_file_list: {}".format(target_file_list))
        for target_file_i in target_file_list:
            file_len = os.path.getsize(target_file_i)
            file_md5 = self.cal_md5(target_file_i)
            file_block_info = file_md5, 0, file_len
            block_id_info = 0, 1
            file_info = (target_file_i, file_block_info, block_id_info)
            print("file_info: {}".format(file_info))
            self.work_queue.put(file_info)

        return self.work_queue.qsize()

    def _pack_data(self, body=None):
        if body is None:
            body_len = self.task_info_len
            msg_body = string_at(addressof(self.task_info), self.task_info_len)
        else:
            body_len = len(body)
            msg_body = body
        self.msg_headers.msg_length = self.msg_headers_len + body_len
        msg_headers = string_at(addressof(self.msg_headers), self.msg_headers_len)
        msg = msg_headers + msg_body
        return msg

    def _unpack_sgw_data(self, data):
        # print("data: {}".format(data))
        if data:
            memmove(addressof(self.msg_headers), data[0: self.msg_headers_len], self.msg_headers_len)
            msg_length = self.msg_headers.msg_length
            if msg_length - self.msg_headers_len == self.task_info_len:
                memmove(addressof(self.task_info), data[self.msg_headers_len:], self.task_info_len)

    def handle_upload(self, sgw_sock, file_obj, file_block_info, source_path):
        md5, start, end = file_block_info
        trans_id = create_trans_id()
        sequence = 0
        self.msg_headers.src_type = 1
        self.msg_headers.src_id = config_info.site_id
        self.msg_headers.dst_type = 3
        self.msg_headers.dst_id = self.task_info.sgw_id
        self.msg_headers.trans_id = trans_id
        self.msg_headers.sequence = sequence
        self.msg_headers.command = 0x20001
        self.msg_headers.total = end - start
        self.task_info.region_id = config_info.region_id
        self.task_info.file_len = end - start
        self.task_info.file_md5 = md5.encode()
        # source_path = self.file_path
        # file_path_in_sgw = '/'.join(source_path.split('/')[2:]).encode()
        file_path_in_sgw = source_path.replace(config_info.upload_path, '', 1).replace(os.sep, '/').lstrip('/').encode()
        # file_path_in_sgw = '/'.join(source_path.split('/')[2:]).encode()
        print("file_path_in_sgw: {}".format(file_path_in_sgw))
        self.task_info.file_name = file_path_in_sgw
        upload_res = False
        try:
            # logger.debug('ready to send upload request to sgw')
            self.msg_headers.ack_code = 0x0  # 应答码清零
            sgw_sock.sendall(self._pack_data())
            # logger.debug('sent upload request to sgw')
            self._unpack_sgw_data(sgw_sock.recv(2048))
            # logger.debug('receive response from sgw')
            if self.msg_headers.ack_code == 200:
                sent_size = 0
                # logger.info("Sending...")
                fault_times = 0
                file_obj.seek(start, 0)
                file_len = end - start
                while True:
                    block_data = file_obj.read(4 * 1024)
                    block_size = len(block_data)
                    if sent_size + block_size > file_len:
                        block_data = block_data[0: file_len - sent_size]
                        block_size = len(block_data)
                    self.msg_headers.trans_id = trans_id
                    sequence += 1
                    self.msg_headers.sequence = sequence
                    self.msg_headers.command = 0x20003
                    self.msg_headers.offset = sent_size
                    self.msg_headers.count = block_size
                    self.msg_headers.ack_code = 0x0  # 应答码清零
                    sgw_sock.sendall(self._pack_data(block_data))
                    recv_data = sgw_sock.recv(2048)
                    if not recv_data:  # 对端主动断开连接或接收超时，''为断开，None为超时
                        raise socket.error('receive data from storage gateway is {}'.format(repr(recv_data)))
                    self._unpack_sgw_data(recv_data)
                    if self.msg_headers.ack_code == 200:
                        if sent_size >= file_len:
                            break
                        sent_size += block_size
                        fault_times = 0
                    else:
                        file_obj.seek(-block_size, 1)  # 文件指针从当前位置往前移
                        sequence -= 1
                        fault_times += 1
                    if fault_times > 10:
                        break
                self.msg_headers.command = 0x20005
                self.msg_headers.ack_code = 0x0  # 应答码清零
                self.task_info.file_md5 = md5.encode()
                sgw_sock.sendall(self._pack_data(b''))
                self._unpack_sgw_data(sgw_sock.recv(2048))
                if self.msg_headers.ack_code == 200:
                    upload_res = True
            else:
                print("sgw ack code error: {}".format(self.msg_headers.ack_code))
        except Exception as upload_error:
            print("upload_error: {}".format(upload_error))
        return upload_res

    def start_to_upload(self):
        file_nums = self.work_queue.qsize()
        sgw_sock = utils.create_client_socket(config_info.sgw_host, config_info.sgw_port)
        while True:
            if self.work_queue.qsize() == 0:
                print("upload task finished.")
                # 通知mds study上传完成
                break
            source_path, file_block_info, block_id_info = self.work_queue.get()
            _, _, file_size = file_block_info
            if file_size > self.MD5_BLOCK_SIZE:
                file_obj = open(source_path, 'rb')
            else:
                with open(source_path, 'rb') as fr:
                    file_obj = io.BytesIO(fr.read())
            cnt = 0
            while cnt <= 3:
                cnt += 1
                self.handle_upload(sgw_sock, file_obj, file_block_info, source_path)
                # if Upload(source_path).upload_file(sgw_sock, file_obj, file_block_info):
                break
            else:
                print("upload {} failed.".format(source_path))
            file_obj.close()
        sgw_sock.close()

        return file_nums


def create_trans_id():
    # trans_id = uuid.uuid1().int >> 64
    trans_id = int(str(int(time.time())) + str(random.getrandbits(32)))
    return trans_id


def download(save_path, sgw_path, file_size):
    handle_common = HandleCommon(config_info.site_id)
    download_req_trans_id = create_trans_id()
    handle_common.task_info = TaskInfo()
    sgw_ip = socket.ntohl(struct.unpack("I", socket.inet_aton(config_info.sgw_host))[0])
    sgw_port = config_info.sgw_port
    handle_common.task_info.sgw_ip = sgw_ip
    handle_common.task_info.sgw_port = sgw_port
    handle_common.task_info.proxy_ip = sgw_ip
    handle_common.task_info.proxy_port = sgw_port
    file_path_in_sgw = sgw_path
    handle_common.task_info.file_name = file_path_in_sgw

    handle_common.msg_headers.src_type = 1
    handle_common.msg_headers.dst_type = 3
    handle_common.msg_headers.dst_id = handle_common.task_info.proxy_id
    handle_common.msg_headers.trans_id = download_req_trans_id
    handle_common.msg_headers.sequence = 0
    # sgw_sock = handle_common.connect_sgw()
    sgw_sock = utils.create_client_socket(config_info.sgw_host, int(sgw_port))

    with open(save_path, 'w+b') as fp:
        handle_common.msg_headers.command = 0x20011
        handle_common.msg_headers.total = file_size
        handle_common.msg_headers.offset = 0
        handle_common.msg_headers.count = file_size
        sgw_sock.sendall(handle_common.pack_data())
        head_msg = recv_cycle(sgw_sock, sizeof(c_longlong))
        msg_length, = struct.unpack(b'>q', head_msg)
        body_msg = recv_cycle(sgw_sock, msg_length - sizeof(c_longlong))
        recv_bytes = head_msg + body_msg
        if recv_bytes:
            file_bytes = recv_bytes[sizeof(c_longlong):]
            if file_bytes:
                fp.write(file_bytes)
                download_res = True
            else:
                print('下载文件为空')
                download_res = False
        else:
            print('下载文件出错')
            download_res = False
    sgw_sock.close()
    return download_res


def recv_cycle(sock, header_length):
    # timeout=None时一直等，超时不会异常
    aim_length = header_length
    data = b''
    for i in range(0, 5):
        receive_msg = sock.recv(aim_length)
        if not receive_msg:
            raise Exception('client disconnect.')
        data += receive_msg
        if len(data) < header_length:
            aim_length = (header_length - len(data))
        else:
            break
    return data


def get_file_list_from_sgw(folder):
    handle_common = HandleCommon(config_info.site_id)

    get_file_list_trans_id = create_trans_id()
    sgw_ip = socket.ntohl(struct.unpack("I", socket.inet_aton(config_info.sgw_host))[0])
    sgw_port = int(config_info.sgw_port)
    handle_common.task_info.sgw_ip = sgw_ip
    handle_common.task_info.sgw_port = sgw_port
    handle_common.task_info.proxy_ip = sgw_ip
    handle_common.task_info.proxy_port = sgw_port
    handle_common.task_info.file_name = folder.encode()
    handle_common.task_info.metadata = b''
    sequence = 0

    handle_common.msg_headers.src_type = 1
    handle_common.msg_headers.dst_type = 3
    handle_common.msg_headers.dst_id = handle_common.task_info.proxy_id
    handle_common.msg_headers.command = 0x2000F
    handle_common.msg_headers.trans_id = get_file_list_trans_id
    handle_common.msg_headers.sequence = sequence

    sgw_sock = utils.create_client_socket(config_info.sgw_host, sgw_port)
    send_data = handle_common.pack_data()
    sgw_sock.sendall(send_data)

    head_msg = recv_cycle(sgw_sock, sizeof(c_longlong))
    msg_length, = struct.unpack(b'>q', head_msg)
    body_msg = recv_cycle(sgw_sock, msg_length - sizeof(c_longlong))
    sgw_sock.close()
    recv_bytes = head_msg + body_msg
    if not recv_bytes:
        print('sgw socket receive result is %s' % recv_bytes)
        return {}
    file_info_bytes = recv_bytes[sizeof(c_longlong):]
    file_num, = struct.unpack(b'>I', file_info_bytes[0: sizeof(c_uint)])
    file_list_bytes = file_info_bytes[sizeof(c_uint):]
    file_info_dict = {}
    for _ in range(file_num):
        file_path_len, = struct.unpack(b'>H', file_list_bytes[0: sizeof(c_ushort)])
        file_size_cursor = sizeof(c_ushort) + file_path_len
        file_path = file_list_bytes[sizeof(c_ushort): file_size_cursor]
        file_size, = struct.unpack(b'>q',
                                   file_list_bytes[file_size_cursor: file_size_cursor + sizeof(c_longlong)])
        file_info_dict[file_path] = file_size
        file_list_bytes = file_list_bytes[file_size_cursor + sizeof(c_longlong):]
    return file_num, file_info_dict


def move_back_notify(send_msg):
    handle_common = HandleCommon(config_info.site_id)
    mds_sock = utils.create_client_socket(config_info.host, config_info.mds_port)
    trans_id = create_trans_id()
    handle_common.msg_headers.command = 0x0014
    handle_common.msg_headers.trans_id = trans_id
    body = json.dumps(send_msg)
    msg = handle_common.pack_data(body.encode())
    mds_sock.sendall(msg)
    header_structure = MsgHeaders()
    header_len = sizeof(header_structure)
    head_msg = recv_cycle(mds_sock, header_len)
    msg_length, = struct.unpack(b'>I', head_msg[0:sizeof(c_uint32)])
    if msg_length - header_len > 0:
        body_msg = recv_cycle(mds_sock, msg_length - header_len)
    mds_sock.close()
    memmove(addressof(header_structure), head_msg, header_len)
    if header_structure.ack_code == 200:
        print("notice MOVE_BACK_NOTIFY to metadata success.")
    elif header_structure.ack_code == 404:
        print("notice MOVE_BACK_NOTIFY to metadata failed.")


def write_study_to_database():
    # 1.查询满足条件的study列表
    study_file = config_info.study_upload_conf
    # study_file = input("study list absolute file_path: ")
    with open(study_file) as fp:
        study_data = fp.readlines()
    study_list = []
    insert_time = "2000-01-01 00:00:00"
    for study_i in study_data:
        if study_i.strip():
            study_list.append((study_i.strip(), insert_time))
    if not study_list:
        print("not found the study id")
        sys.exit(-1)
    mds_host = config_info.host
    mds_db = config_info.db
    mds_user = config_info.user
    mds_passwd = config_info.password
    print("insert into metadata database begin")
    conn = pymysql.connect(host=mds_host, user=mds_user, passwd=mds_passwd, db=mds_db, charset='utf8mb4')
    cursor = conn.cursor()
    sql = "INSERT INTO study_index6 (study_id, create_time) VALUES(%s, %s)"
    print("study_list: {}".format(study_list))
    cursor.executemany(sql, study_list)
    conn.commit()
    cursor.close()
    conn.close()
    print("insert into metadata database end")

def test_client_download():
    # 下载 begin
    # 1.获取需要下载的study列表
    download_study = config_info.study_download_conf
    with open(download_study) as fp:
        file_data = fp.readlines()
    file_list = []
    for file_i in file_data:
        if file_i.strip():
            file_list.append(file_i.strip().lower())

    # print("file_list: {}".format(file_list))
    for download_file in file_list:
        study_id = download_file.split('/')[0]
        file_num, all_files = get_file_list_from_sgw(study_id)
        print("file_num: {}".format(file_num))
        print("all_files: {}".format(all_files))
        print("准备回迁{study_name}下的{count}个文件".format(
            study_name=study_id,
            count=file_num
        ))
        download_tasks = []
        for k, v in all_files.items():
            save_path = os.path.join(config_info.download_path, k.decode().replace('/', os.sep).lstrip(os.sep))
            parent_path = save_path.rsplit(os.sep, 1)[0]
            download_tasks.append({
                'file_path': k,
                'save_path': save_path,
                'file_size': v
            })
            if not os.path.exists(parent_path):
                os.makedirs(parent_path)
            ret = download(save_path, k, v)
            if not ret:
                print("{study_name}回迁失败".format(study_name=study_id))
                break
        else:
            print("{study_name}下的文件已回迁完成".format(study_name=study_id))
            msg = {'study_id': study_id}
            move_back_notify(msg)


def test_client_upload():
    print("upload start_time: {}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    upload_tasks = []
    for i in range(0, config_info.upload_nums):
        t = Process(target=upload_single_task)
        upload_tasks.append(t)
    for upload_task in upload_tasks:
        upload_task.start()
    for upload_task in upload_tasks:
        upload_task.join()
    print("upload end_time: {}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))


def upload_single_task():
    while True:
        mds_host = config_info.host
        mds_tcp_port = config_info.mds_port
        clisock = utils.create_client_socket(mds_host, int(mds_tcp_port))

        cli_obj = HandleCommon(config_info.site_id)
        cli_obj.msg_headers.command = 0x0010
        cli_obj.msg_headers.trans_id = create_trans_id()
        time_a = time.strptime('2000-01-01 00:00:01', "%Y-%m-%d %H:%M:%S")
        time_send = int(time.mktime(time_a))
        query_param = {
            'timestamp_before': time_send,
            'study_state': 0,
            'nr_study': 5,
            'study_id': '',
            'nr_files': 0
        }
        # header

        body = json.dumps(query_param)

        msg = cli_obj.pack_data(body.encode())
        clisock.sendall(msg)

        _, _, _, body = utils.get_msg(clisock, config.Constant.HEAD_LENGTH, config.Constant.FMT_COMMON_HEAD)
        upload_study_list = json.loads(body.decode())['study_list']
        print("upload_study_list: {}".format(upload_study_list))

        study_absolute_path_l = []
        for upload_i in upload_study_list:
            absolute_path = os.path.join(config_info.upload_path, study_id_to_path(upload_i), upload_i)
            study_absolute_path_l.append(absolute_path)

            # 构建消息体
            upload_obj = Upload(absolute_path)
            upload_obj.queue_create()
            counts = upload_obj.start_to_upload()
            query_param = {
                'timestamp_before': 0,
                'study_state': 0,
                'nr_study': 0,
                'study_id': upload_i,
                'nr_files': counts
            }
            cli_obj = HandleCommon(config_info.site_id)
            cli_obj.msg_headers.command = 0x0010
            cli_obj.msg_headers.trans_id = create_trans_id()
            body = json.dumps(query_param)

            msg = cli_obj.pack_data(body.encode())
            clisock.sendall(msg)
        clisock.close()
        if not upload_study_list:
            break


def test_client_query_file_number():
    args_filepath = config_info.study_upload_conf
    # args_filepath = input("request(json absolute filepath): ")
    with open(args_filepath) as fin:
        query_body_unpack = json.load(fin)
        print(json.dumps(query_body_unpack, indent=4, ensure_ascii=False))
    query_body_pack = json.dumps(query_body_unpack).encode("utf-8")
    query_body_size = len(query_body_pack)

    head_size = struct.calcsize(config.Constant.FMT_COMMON_HEAD)
    total_size = head_size + query_body_size

    # header
    t_header = Header()
    t_header.total_size = total_size
    t_header.command = config.Constant.CLIENT_QUERY_NUM
    header_pack = t_header.pack()

    # packet
    pkt = header_pack + query_body_pack

    # send request
    host = input("host: ")
    port = input("port: ")
    clisock = utils.create_client_socket(host, int(port))
    clisock.sendall(pkt)

    # recv response
    recvlen, header_pack = utils.attempt_recvall(clisock,
                                                 config.Constant.HEAD_LENGTH)
    if recvlen == config.Constant.HEAD_LENGTH:
        header_unpack = struct.unpack(config.Constant.FMT_COMMON_HEAD,
                                      header_pack)
        print("nr_files:", header_unpack[11])
        print("test_client_query_file_num: OK")
    else:
        print("test_client_query_file_num: FAIL (recv uncompleted message)")


def test_client_query_file_data():
    args_filepath = input("request(json absolute filepath): ")
    with open(args_filepath) as fin:
        query_body_unpack = json.load(fin)
        print(json.dumps(query_body_unpack, indent=4, ensure_ascii=False))
    query_body_pack = json.dumps(query_body_unpack).encode('utf-8')
    query_body_size = len(query_body_pack)

    head_size = struct.calcsize(config.Constant.FMT_COMMON_HEAD)
    total_size = head_size + query_body_size

    # header
    t_header = Header()
    t_header.total_size = total_size
    t_header.command = config.Constant.CLIENT_QUERY_DATA
    header_pack = t_header.pack()

    # packet
    pkt = header_pack + query_body_pack

    # send request
    host = input("host: ")
    port = input("port: ")
    clisock = utils.create_client_socket(host, int(port))
    clisock.sendall(pkt)

    def parse(entry):
        fixlen = struct.calcsize(config.Constant.FMT_TASKINFO_FIXED)
        body_pack = entry[:fixlen]
        body_unpack = struct.unpack(config.Constant.FMT_TASKINFO_FIXED,
                                    body_pack)
        metalen = body_unpack[15]
        return (fixlen, metalen)

    def output(meta_unpack):
        print("user_id:", meta_unpack.get("user_id"))
        print("customer_id:", meta_unpack.get("customer_id"))
        print("file_path:", meta_unpack.get("file_path"))
        print("file_name:", meta_unpack.get("file_name"))
        print("file_md5:", meta_unpack.get("file_md5"))
        print("thumb_md5", meta_unpack.get("thumb_md5"))
        print("nr_blocks:", meta_unpack.get("nr_blocks"))
        blocks = meta_unpack.get("blocks")
        for block_id, block_md5 in enumerate(blocks):
            print("block: {0} {1} {2}".format(
                block_id, block_md5, meta_unpack.get(block_md5)
            ))
        print("auto_examine:", meta_unpack.get("auto_examine"))
        print("text:", meta_unpack.get("text"))
        examine_details = meta_unpack.get("examine_details")
        if examine_details:
            for detail in examine_details:
                print("word: {0}, time: {1}".format(
                    detail.get("word"), detail.get("time")
                ))

    def parse_and_output(pkt):
        while len(pkt) > 0:
            fixlen, metalen = parse(pkt)

            meta_pack = pkt[fixlen:fixlen+metalen]
            meta_unpack = json.loads(meta_pack.decode('utf-8'))

            output(meta_unpack)

            pkt = pkt[fixlen+metalen:]


    # recv response
    hdrlen, header_unpack, bodylen, body_pack = utils.get_msg(
        clisock, config.Constant.HEAD_LENGTH, config.Constant.FMT_COMMON_HEAD
    )
    if header_unpack:
        ack_code = header_unpack[10]
        if int(ack_code) == 200:
            if body_pack:
                parse_and_output(body_pack)
                print("test_client_query_data: OK")
            else:
                print("test_client_query_data: OK (no file metadata)")
        else:
            print("test_client_query_file_data: FAIL (ack={0})".format(
                ack_code))
    else:
        print("test_client_query_file_data: FAIL (uncompleted header)")


def test_client_delete():
    args_filepath = input("request(json absolute filepath): ")
    with open(args_filepath) as fin:
        query_body_unpack = json.load(fin)
        print(json.dumps(query_body_unpack, indent=4, ensure_ascii=False))

    site_id = query_body_unpack.get("site_id")
    app_id = query_body_unpack.get("app_id")
    timestamp = query_body_unpack.get("timestamp")
    file_name = query_body_unpack.get("file_name").encode("utf-8")
    file_md5  = query_body_unpack.get("file_md5").encode("utf-8")

    # body
    t_body = Body()
    t_body.site_id = int(site_id)
    t_body.app_id = int(app_id)
    t_body.timestamp = int(timestamp)
    t_body.file_name = file_name
    t_body.file_md5 = file_md5
    body_pack = t_body.pack()
    body_size = len(body_pack)

    # meta
    del query_body_unpack["site_id"]
    del query_body_unpack["app_id"]
    del query_body_unpack["timestamp"]
    del query_body_unpack["file_name"]
    del query_body_unpack["file_md5"]
    query_body_pack = json.dumps(query_body_unpack).encode("utf-8")
    query_body_size = len(query_body_pack)

    # header
    t_header = Header()
    t_header.command = config.Constant.CLIENT_DEL
    head_size = struct.calcsize(config.Constant.FMT_COMMON_HEAD)
    t_header.total_size = head_size + body_size + query_body_size
    header_pack = t_header.pack()

    # packet
    pkt = header_pack + body_pack + query_body_pack

    # send request
    host = input("host: ")
    port = input("port: ")
    clisock = utils.create_client_socket(host, int(port))
    clisock.sendall(pkt)

    # recv response
    recvlen, header_pack = utils.attempt_recvall(clisock,
                                                 config.Constant.HEAD_LENGTH)
    if recvlen == config.Constant.HEAD_LENGTH:
        header_unpack = struct.unpack(config.Constant.FMT_COMMON_HEAD,
                                      header_pack)
        ack_code = header_unpack[10]
        if int(ack_code) == 200:
            print("test_client_delete: OK")
        else:
            print("test_client_delete: FAIL (ack={0})".format(ack_code))
    else:
        print("test_client_delete: FAIL (recv uncompleted message)")


def test_migration_start():
    args_filepath = input("request(json absolute filepath): ")
    with open(args_filepath) as fin:
        migoption = json.load(fin)
        print(json.dumps(migoption, indent=4, ensure_ascii=False))

    old_sgw_ip   = migoption.get("old_sgw_ip").encode("utf-8")
    old_sgw_port = migoption.get("old_sgw_port")
    new_sgw_ip   = migoption.get("new_sgw_ip").encode("utf-8")
    new_sgw_port = migoption.get("new_sgw_port")
    old_mds_ip   = migoption.get("old_mds_ip").encode("utf-8")
    old_mds_port = migoption.get("old_mds_port")
    new_mds_ip   = migoption.get("new_mds_ip").encode("utf-8")
    new_mds_port = migoption.get("new_mds_port")

    # payload
    fmt_migoption = "!64sH64sH64sH64sH"
    migoption_unpack = (
        old_sgw_ip, old_sgw_port, new_sgw_ip, new_sgw_port,
        old_mds_ip, old_mds_port, new_mds_ip, new_mds_port
    )
    migoption_pack = struct.pack(fmt_migoption, *migoption_unpack)
    print("migoption_pack size: ", struct.calcsize(fmt_migoption))
    print("migoption_pack len:  ", len(migoption_pack))

    # Header
    t_header = Header()
    t_header.total_size = 64 + len(migoption_pack)
    t_header.command = 0x00030001
    header_pack = t_header.pack()

    # packet
    pkt = header_pack + migoption_pack

    # send request to sgw
    clisock = utils.create_client_socket(old_sgw_ip, old_sgw_port)
    clisock.sendall(pkt)

    # recv response
    recvlen, header_pack = utils.attempt_recvall(
        clisock, config.Constant.HEAD_LENGTH
    )
    if recvlen == config.Constant.HEAD_LENGTH:
        header_unpack = struct.unpack(
            config.Constant.FMT_COMMON_HEAD, header_pack
        )
        ack_code = header_unpack[10]
        if int(ack_code) == 200:
            print("test_migration_start: OK")
        else:
            print("test_migration_start: FAIL (ack={0})".format(ack_code))
    else:
        print("test_migration_start: FAIL (recv uncompleted message)")

def quit():
    sys.exit(0)

actions = collections.OrderedDict(
    [("1", test_client_upload),
     ("2", test_client_download),
     ("3", write_study_to_database),
     # ("3", test_client_query_file_data),
     # ("4", test_client_delete),
     # ("5", test_migration_start),
     ("q", quit)]
)

def hint():
    print("====")
    for name, action in actions.items():
        print(name, action.__name__)
    print("====")
    print("Please input: ")

def main():
    while True:
        hint()
        x = raw_input()
        if x in actions.keys():
            action = actions[x]
            action()
        else:
            print("invalid input action {0}".format(x))



if __name__ == '__main__':
    import sys
    try:
        main()
    except KeyboardInterrupt:
        sys.exit("keyboard interrupt")
