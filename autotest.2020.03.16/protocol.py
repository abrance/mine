# -*- coding: utf-8 -*-

# 将消息之间的交互都集中放在这里。

# mike
# 2019-12-09

import time, datetime
import socket, struct, json

import utils
import config, message

hdrlen = config.Constant.HEAD_LENGTH
tsklen = config.Constant.TASKINFO_LENGTH

class Protocol(object):
    def __init__(
        self,
        sgw_addr="127.0.0.1", sgw_port=7788,
        mds_addr="127.0.0.1", mds_port=8899
    ):
        self.sgw_addr = sgw_addr
        self.sgw_port = sgw_port
        self.timestamp_before = int(time.time())
        self.agent_id = 1209
        self.nr_study = 10
        self.study_state = 1
        self.nr_files = 0
        self.study_id = ""
        self.sock = None

    def set_timestamp_before(self, timestamp_before):
        self.timestamp_before = timestamp_before

    def set_agent_id(self, agent_id):
        self.agent_id = agent_id

    def set_study_state(self, study_state):
        self.study_state = study_state

    def launch(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.sgw_addr, self.sgw_port))

    def recv_packet(self, size=4):
        assert size == 4 or size == 8
        block = self.sock.recv(size)
        if block:
            packet = b''
            packet += block
            if size == 4:
                left = struct.unpack("!I", block)[0]
            else:
                left = struct.unpack("!Q", block)[0]
            left -= size # 已接收 size 个字节的消息长度
            while left > 0:
                recvlen, block = utils.attempt_recvall(self.sock, left)
                if recvlen > 0:
                    packet += block
                    left -= recvlen
                else:
                    break
            return packet
        else:
            return b''

    def _recvrs_common1(self):
        pkt = self.recv_packet()
        H = pkt[0:config.Constant.HEAD_LENGTH]
        h = message.Header.unpack(H)
        if h.ack_code == 200:
            return True
        else:
            return False

    def _recvrs_common2(self, expect_command, expect_ack_code=200):
        """接收文件结束下载请求的响应"""
        pkt = self.recv_packet()
        H = pkt[0:hdrlen]
        h = message.Header.unpack(H)
        if h.command == expect_command:
            if h.ack_code == expect_ack_code:
                return True
            else:
                print("ack_code: {} expect, {} recved".format(
                    expect_ack_code, h.ack_code
                ))
                return False
        else:
            print("command: 0x{:x} expect, 0x{:x} recved".format(
                expect_command, h.command
            ))
            return False

    def _sendrq1(self, filepath):
        """文件开始上传请求"""
        t = message.Taskinfo()
        t.sgw_ip = message.ipv4_to_int(self.sgw_addr)
        t.file_md5 = utils.calcmd5(filepath).encode("utf-8")
        import os
        sendpath = filepath.replace(os.sep, "/")
        t.file_name = sendpath.encode("utf-8")
        T = t.pack()

        # header
        h = message.Header()
        h.command = 0x00020001
        h.total_size = hdrlen + tsklen
        import os
        h.total = os.stat(filepath).st_size
        h.offset = 0
        h.count = 1
        H = h.pack()

        # entire packet
        pkt = H + T

        # send
        self.sock.sendall(pkt)

    def _recvrs1(self):
        """文件开始上传请求的响应"""
        return self._recvrs_common1()

    def _sendrq2(self, offset, block):
        """文件内容上传请求"""
        blocklen = len(block)
        h = message.Header()
        h.command = 0x00020003
        h.total_size = hdrlen + blocklen
        h.offset = offset
        h.count = blocklen
        H = h.pack()
        pkt = H + block
        self.sock.sendall(pkt)

    def _recvrs2(self):
        """文件内容上传请求的响应"""
        return self._recvrs_common1()

    def _sendrq3(self):
        """文件结束上传请求"""
        h = message.Header()
        h.command = 0x00020005
        h.total_size = hdrlen
        H = h.pack()
        self.sock.sendall(H)

    def _recvrs3(self):
        """文件结束上传请求的响应"""
        return self._recvrs_common1()

    def _sendrq4(self, filepath):
        """顺序下载文件请求"""
        h = message.Header()
        h.command = 0x00020011
        h.total_size = hdrlen + tsklen
        H = h.pack()

        t = message.Taskinfo()
        t.file_name = filepath.encode("utf-8")
        T = t.pack()

        pkt = H + T
        self.sock.sendall(pkt)

    def _recvrs4_content(self, filepath):
        """接收顺序下载文件的内容"""
        block1 = self.sock.recv(40)
        msglen, md5_recv = struct.unpack("!q32s", block1)
        assert len(md5_recv) == 32
        # print("msglen: {}, md5: {}".format(msglen, md5_recv))

        blocksize = 4096
        left = msglen - 40 # 32+8
        with open(filepath, "wb") as f:
            while left > 0:
                want = blocksize if left >= blocksize else left
                fileblob = self.sock.recv(want)
                if fileblob:
                    f.write(fileblob)
                    left -= len(fileblob)
                else:
                    break
        return md5_recv

    def _recvrs4(self, filepath):
        """顺序下载文件的消息包格式：

        (msglen, 8) (md5, 32) (file content, ...)

        第一部分：消息包总长度，8 个字节
        第二部分：md5 校验和的长度，32 字节
        第三部分：文件内容，长度是 msglen-8-32

        (140) (32) (100)
        """
        md5_recv = self._recvrs4_content(filepath)
        md5_save = utils.calcmd5(filepath).encode("utf-8")
        if len(md5_recv) == len(md5_save):
            if md5_recv == md5_save:
                return True
            else:
                print("md5_recv and md5_save content mismatch!".format())
                print("md5_recv: {}".format(md5_recv))
                print("md5_save: {}".format(md5_save))
                return False
        else:
            print("md5_recv and md5_save length not equal!")
            print("md5_recv: {}".format(md5_recv))
            print("md5_save: {}".format(md5_save))
            return False

    def _sendrq5(self, study_state):
        """查询 studyid 列表请求"""
        x = dict()
        x["timestamp_before"] = int(time.time())
        x["study_state"] = study_state
        x["agent_id"] = self.agent_id
        x["nr_study"] = self.nr_study
        x["study_id"] = "from-test-program"
        x["nr_files"] = 0
        X = json.dumps(x).encode("utf-8")

        h = message.Header()
        h.command = 0x00000010
        h.total_size = 64 + len(X)
        h.src_id = self.agent_id
        H = h.pack()

        pkt = H + X
        self.sock.sendall(pkt)

    def _recvrs5(self):
        """查询 studyid 列表请求的响应"""
        m = self.recv_packet()
        X = m[64:]
        x = json.loads(X.decode("utf-8"))
        return x

    def _sendrq6(self, study_state):
        """查询 studyid 列表请求（版本 2）"""
        x = dict()
        dt = datetime.datetime.strptime("2010-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")
        x["agent_id"] = self.agent_id
        x["timestamp_beg"] = int(dt.timestamp())
        x["timestamp_end"] = int(time.time())
        x["study_state"] = study_state
        x["nr_study"] = self.nr_study
        X = json.dumps(x).encode("utf-8")

        h = message.Header()
        h.command = 0x00000028
        h.total_size = 64 + len(X)
        h.src_id = self.agent_id
        H = h.pack()

        pkt = H + X
        self.sock.sendall(pkt)

    def _recvrs6(self):
        """查询 studyid 列表请求（版本 2）的响应"""
        P = self.recv_packet()
        if P:
            H = P[0:64]
            h = message.Header.unpack(H)
            if h.command == 0x00000029:
                if h.ack_code == config.Constant.ACK_SUCCESS:
                    X = P[64:]
                    x = json.loads(X.decode("utf-8"))
                    return (True, x)
                else:
                    print("command failed: ack code {}".format(h.ack_code))
                    return (False, b'ack code failed')
            else:
                print("invalid command: 0x{0:x}".format(h.command))
                return (False, b'invalid command')
        else:
            return (False, b'recv packet failed')

    def _sendrq7(self, finish_list):
        """上传 studyid 成功通知请求"""
        x = dict()
        x["nr_upload"] = len(finish_list)
        x["upload_list"] = finish_list
        X = json.dumps(x).encode("utf-8")

        h = message.Header()
        h.command = 0x00000026
        h.total_size = 64 + len(X)
        h.src_id = self.agent_id
        H = h.pack()

        pkt = H + X
        self.sock.sendall(pkt)

    def _recvrs7(self):
        """上传 studyid 成功通知请求的响应"""
        H = self.recv_packet()
        hdrlen = len(H)
        if hdrlen == 64:
            h = message.Header.unpack(H)
            if h.command == 0x00000027:
                if h.ack_code == 200:
                    return True
                else:
                    print("command failed: ack code {}".format(h.ack_code))
                    return False
            else:
                print("unexpect command 0x{0:x}".format(h.command))
                return False
        else:
            print("unexpect header length:", hdrlen)
            return False

    def _sendrq8(self, delete_list):
        """删除客户端中 studyid 下文件的通知请求"""
        x = dict()
        x["nr_delete"] = len(delete_list)
        x["delete_list"] = delete_list
        X = json.dumps(x).encode("utf-8")

        h = message.Header()
        h.command = 0x00000024
        h.total_size = 64 + len(X)
        h.src_id = self.agent_id
        H = h.pack()

        pkt = H + X
        self.sock.sendall(pkt)

    def _recvrs8(self):
        """删除客户端中 studyid 下文件的通知请求的响应"""
        H = self.recv_packet()
        hdrlen = len(H)
        if hdrlen == 64:
            h = message.Header.unpack(H)
            if h.command == 0x00000025:
                if h.ack_code == 200:
                    return True
                else:
                    print("command failed: ack code {}".format(h.ack_code))
                    return False
            else:
                print("unexpect command 0x{0:x}".format(h.command))
                return False
        else:
            print("unexpect header length:", hdrlen)
            return False

    def _sendrq9(self, studyid):
        """发送获取 studyid 列表请求"""
        h = message.Header()
        h.command = 0x0002000F
        h.total_size = hdrlen + tsklen
        H = h.pack()

        t = message.Taskinfo()
        t.file_name = studyid.encode("utf-8")
        T = t.pack()

        pkt = H + T
        self.sock.sendall(pkt)

    def _recvrs9(self):
        """接受获取 studyid 列表的响应

        响应的消息格式：

        (msglen) (nrfiles) (namelen filename filesize) ...

        msglen: 整个消息包的长度，8 个字节
        nrfiles: 消息包包含的文件个数，4 个字节
        namelen: 文件名长度，2 个字节
        filename: 由 namelen 的值决定
        filesize: 文件大小，8 个字节

        例子：

        (54) (3) (5 hello 12) (3 abc 123) (4 1234 4096)

        上面的例子给出的消息格式解释：消息包有 54 个字节，消息包内包含
        3 个文件。第一个文件的文件名有 5 个字节，文件名是“hello”，文件
        大小是 12 个字节；第二个文件的文件名有 3 个字节，文件名是“abc”，
        文件大小有 123 个字节；第三个文件的文件名有 4 个字节，文件名是
        “1234”，文件大小 4096 个字节。

        接收到响应后，返回给调用者的是一个字典结构，形如：

        {"msglen": 54, "nrfiles": 3, "filelist": [
                {"filename": "hello", "filesize": 12},
                {"filename": "abc", "filesize": 123},
                {"filename": "1234", "filesize": 4096}
            ]
        }

        """
        block = self.recv_packet(8)
        # 正常至少 10 个字节，8 个字节的消息长度，2 个字节的文件个数
        assert len(block) >= 10

        r = {}

        p1 = block[0:8]
        msglen = struct.unpack("!Q", p1)[0]
        r["msglen"] = msglen

        p2 = block[8:12]
        nrfiles = struct.unpack("!I", p2)[0]
        r["nrfiles"] = nrfiles

        p3 = block[12:]
        filelist = {}
        while len(p3) > 0:
            p4 = p3[0:2]
            namelen = struct.unpack("!H", p4)[0]
            p5 = p3[2:2+namelen]
            filename = p5.decode("utf-8")
            p6 = p3[2+namelen:2+namelen+8]
            filesize = struct.unpack("!Q", p6)[0]
            filelist[filename] = filesize
            p3 = p3[2+namelen+8:]
        r["filelist"] = filelist

        return r

    def _sendrq10(self, filepath):
        """发送文件开始下载请求"""
        # taskinfo
        t = message.Taskinfo()
        t.sgw_ip = message.ipv4_to_int(self.sgw_addr)
        t.file_name = filepath.encode("utf-8")
        T = t.pack()

        # header
        h = message.Header()
        h.command = 0x00020007
        h.total_size = hdrlen + tsklen
        H = h.pack()

        # send
        self.sock.sendall(H + T)

    def _recvrs10(self):
        """接收发送文件开始下载请求的响应

        函数的返回值是一个元组：（错误码，文件大小）"""
        pkt = self.recv_packet()
        H = pkt[0:hdrlen]
        h = message.Header.unpack(H)
        if h.command == 0x00020008:
            if h.ack_code == 200:
                return (True, h.total)
            else:
                return (False, -1)
        else:
            return (False, -1)

    def _sendrq11(self, offset, count):
        """发送下载文件内容请求，从偏移 offset 处下载 count 个字节"""
        # header
        h = message.Header()
        h.command = 0x00020009
        h.offset = offset
        h.count = count
        h.total_size = hdrlen
        H = h.pack()
        # send
        self.sock.sendall(H)

    def _recvrs11(self):
        """接收下载文件内容请求的响应"""
        pkt = self.recv_packet()
        H = pkt[0:hdrlen]
        h = message.Header.unpack(H)
        if h.command == 0x0002000A:
            if h.ack_code == 200:
                blob = pkt[hdrlen:]
                len1 = len(blob)
                len2 = h.total_size - hdrlen
                if len1 == len2:
                    return (True, blob)
                else:
                    print("_recvrs11: mismatch blob length {}/{}".format(
                        len1, len2
                    ))
                    return (False, b'')
            else:
                print("_recvrs11: unexpect ack code {}".format(h.ack_code))
                return (False, b'')
        else:
            print("_recvrs11: unexpect command 0x{:x}".format(h.command))
            return (False, b'')

    def _sendrq12(self):
        """发送文件结束下载请求"""
        h = message.Header()
        h.command = 0x0002000B
        h.total_size = hdrlen
        H = h.pack()
        self.sock.sendall(H)

    def _recvrs12(self):
        """接收文件结束下载请求的响应"""
        return self._recvrs_common2(expect_command=0x0002000C)

    def putfile1(self, filepath):
        self._sendrq1(filepath)
        self._recvrs1()
        blocksize = 4096
        offset = 0
        with open(filepath, "rb") as f:
            while True:
                block = f.read(blocksize)
                if block:
                    self._sendrq2(offset, block)
                    self._recvrs2()
                    offset += len(block)
                else:
                    break
        self._sendrq3()
        return self._recvrs3()

    def getfile1(self, filepath):
        self._sendrq4(filepath)
        return self._recvrs4(filepath)

    def getfile2(self, filepath):
        self._sendrq4(filepath)
        return self._recvrs4_content(filepath)

    def getfile3(self, filepath):
        """使用偏移下载接口来下载文件

        偏移下载文件使用三个接口：

        1. 开始下载请求 (1)
        2. 下载文件内容请求，如果文件大小为零，则不需要使用这个接口 (n)
        3. 结束下载请求 (1)

        每个请求都要等待接收到响应之后再发起下一个请求。
        """
        self._sendrq10(filepath)
        rc, filesize = self._recvrs10()
        if rc:
            leftsize = filesize
            blocksize = 8192
            offset = 0
            f = open(filepath, "wb")
            while leftsize > 0:
                count = blocksize if leftsize >= blocksize else leftsize
                self._sendrq11(offset, count)
                rc, blob = self._recvrs11()
                if rc:
                    offset = offset + count
                    leftsize = leftsize - count
                    f.write(blob)
                else:
                    return False
            f.close()
            self._sendrq12()
            return self._recvrs12()
        else:
            return False

    def getfilelist1(self, studyid):
        """获取一个检查下的文件列表"""
        self._sendrq9(studyid)
        return self._recvrs9()

    def query1(self, study_state):
        self._sendrq5(study_state)
        return self._recvrs5()

    def query2(self, study_state):
        self._sendrq6(study_state)
        return self._recvrs6()

    def notify1(self, finish_list):
        self._sendrq7(finish_list)
        return self._recvrs7()

    def notify2(self, delete_list):
        self._sendrq8(delete_list)
        return self._recvrs8()

    def finish(self):
        if self.sock:
            self.sock.close()
        else:
            pass
