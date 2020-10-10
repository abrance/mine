# -*- coding: utf-8 -*-
# utils
import ftplib
from collections import OrderedDict
import time
import os
import threading


class ScanerInitException(Exception):
    def __init__(self):
        Exception.__init__(self)


class Ftp(object):
    """
    文件传输基类 #
    """
    def __init__(self, host, port=21):
        ftp = ftplib.FTP()
        # ftp.set_pasv(False)
        self.ftp = ftp
        self.ftp.encoding = 'gbk'
        self.ftp.connect(host, port)

    def login(self, user, password):
        self.ftp.login(user, password)
        print(self.ftp.welcome)

    def download_file(self, local_file, remote_file):  # 下载指定目录下的指定文件
        file_handler = open(local_file, 'wb')
        print(file_handler)
        # self.ftp.retrbinary("RETR %s" % (RemoteFile), file_handler.write)#接收服务器上文件并写入本地文件
        self.ftp.retrbinary('RETR ' + remote_file, file_handler.write)
        file_handler.close()
        return True

    def download_file_tree(self, local_dir, remote_dir):  # 下载整个目录下的文件
        print("remoteDir:", remote_dir)
        if not os.path.exists(local_dir):
            os.makedirs(local_dir)
        self.ftp.cwd(remote_dir)
        remote_names = self.ftp.nlst()
        print("RemoteNames", remote_names)
        for file in remote_names:
            local = os.path.join(local_dir, file)
            print(self.ftp.nlst(file))
            if file.find(".") == -1:
                if not os.path.exists(local):
                    os.makedirs(local)
                self.download_file_tree(local, file)
            else:
                self.download_file(local, file)
        self.ftp.cwd("..")
        return True

    # 从本地上传文件到ftp
    def upload_file(self, local_path, remote_path):
        buf_size = 1024
        fp = open(local_path, 'rb')
        self.ftp.storbinary('STOR ' + remote_path, fp, buf_size)
        self.ftp.set_debuglevel(0)
        fp.close()

    def upload_dir(self, local_dir, remote_dir):
        print('<<<< upload_dir: local_dir:{} remote_dir:{}'.format(local_dir, remote_dir))
        if not os.path.isdir(local_dir):
            return
        try:
            # 按照目录层级正序 加入到father_dir_ls列表中
            father_dir_ls = []
            _remote_dir = remote_dir
            while os.path.dirname(_remote_dir) != '/':
                _remote_dir = os.path.dirname(_remote_dir)
                father_dir_ls.insert(0, _remote_dir)

            # dir_ls = remote_dir.split('/')[2:]
            # 远程目录下建立目录
            for _dir in father_dir_ls:
                dir_ls = []
                self.ftp.dir(_dir, dir_ls.append)
                if father_dir_ls[-1] == _dir:
                    subdir = remote_dir
                else:
                    subdir = father_dir_ls[father_dir_ls.index(_dir)+1].split('/')[-1]

                    dir_ls = [i.split(' ')[-1] for i in dir_ls if i.split(' ')[-2] == '<DIR>']
                if subdir in dir_ls:
                    continue
                else:
                    try:
                        self.ftp.cwd(_dir)
                        self.ftp.mkd(subdir)
                    except Exception:
                        pass

            # 往 已存在的目录中添加文件
            for file in os.listdir(local_dir):
                try:
                    src_file = os.path.join(local_dir, file)
                    remote_file = os.path.join(remote_dir, file)
                    if os.path.isfile(src_file):
                        self.upload_file(src_file, remote_file)
                    elif os.path.isdir(src_file):
                        self.upload_dir(src_file, remote_file)
                except Exception as e:
                    print('fpt upload error: {}'.format(e))
                    continue
            # self.ftp.cwd('..')
            return True

        except Exception as e:
            print(e)
            return False

    def rename(self, from_name, to_name):
        # 2020/10/10 支持目录和文件
        try:
            self.ftp.rename(from_name, to_name)
        except Exception as e:
            print(e)
            return False

    def close(self):
        self.ftp.quit()


class MyFtp(Ftp):
    """
    文件传输 子类
    """
    def __init__(self):
        super(MyFtp, self).__init__('')
        self.login('', '')


class LRUCache(threading.Thread):
    """不能存储可变类型对象，不能并发访问set()"""
    def __init__(self, capacity, auto_pop=False):
        self.capacity = capacity
        self.cache = OrderedDict()
        self.auto_pop = auto_pop
        super(LRUCache, self).__init__()

    def get(self, key):
        if key in self.cache:
            value = self.cache.pop(key)
            self.cache[key] = value
        else:
            value = None
        return value

    def set(self, key, value):
        if key in self.cache:
            value = self.cache.pop(key)
            self.cache[key] = value
        else:
            if len(self.cache) >= self.capacity:
                self.cache.popitem(last=False)  # pop出第一个item
                self.cache[key] = value
            else:
                self.cache[key] = value

    def pop(self, key):
        if key in self.cache:
            self.cache.pop(key, -1)
        return True

    def add_job(self):
        while True:
            if self.cache:
                self.cache.popitem(last=False)
                time.sleep(15)
            else:
                time.sleep(60)

    def run(self) -> None:
        if self.auto_pop:
            self.add_job()
        else:
            pass


class RecordLRUCache(LRUCache):
    """不能存储可变类型对象，不能并发访问set()"""
    def __init__(self, capacity, auto_pop=False):
        super(RecordLRUCache, self).__init__(capacity, auto_pop)

    def get(self, key):
        if key in self.cache:
            value = self.cache.pop(key)
            self.cache[key] = value

            return value

    def set(self, key, value):
        if key in self.cache:
            value = self.cache.pop(key)
            self.cache[key] = value
        else:
            if len(self.cache) >= self.capacity:
                self.cache.popitem(last=False)  # pop出第一个item
                self.cache[key] = value
            else:
                self.cache[key] = value

    def pop(self, key):
        if key in self.cache:
            self.cache.pop(key)
        return True
