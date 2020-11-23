# -*- coding: utf-8 -*-

"""
# AWS对象存储 调用工具
    python2 实现的， 需安装boto3包
    pip install boto3

    通过兼容AWS 对象存储的平台，调用相应的接口可以实现对象存储，将文件和完整的目录结构存储到云端并可供下载。

    windows下，仅供小小参考
    上传速度：
        131M 23s   平均5.69M/s
        100M 17s   平均5.88M/s
    下载速度：
        131M 8s   平均16.375M/s
        100M 7s   平均14.285M/s
"""

from __future__ import unicode_literals

import os
import time

import boto3
import threading
import Queue
import hashlib
import base64
from datetime import datetime
from boto3.session import Session


class ObjectStorageTest(object):
    def __init__(self, endpoint, access_key, secret_key, bucket_name):
        self.session = boto3.client(
            service_name='s3',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            endpoint_url='http://{}'.format(endpoint),
        )
        self.s3 = boto3.resource(
            service_name='s3',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            endpoint_url='http://{}'.format(endpoint),
            verify=False
        )
        self.bucket = bucket_name

    def create_new_bucket(self, bucket_name):
        self.bucket = self.session.create_bucket(Bucket=bucket_name)

    def get_bucket_by_study(self):
        pass

    def create_new_object(self, file_name, upload_path):
        try:
            with open(file_name, 'rb') as fp:
                data = fp.read()
            md5 = hashlib.md5(data).digest()
            b64_md5 = base64.b64encode(md5)
            # self.s3.Bucket(self.bucket).upload_file(file_name, upload_path)
            self.s3.Bucket(self.bucket).put_object(
                Body=open(file_name, 'rb'),
                Key=upload_path,
                ContentMD5=b64_md5,
                Metadata={
                    'md5checksum': b64_md5
                },
            )
        except Exception as e:
            print(e)
        return True
        # if os.path.exists(file_name):
        #     fp = open(file_name, 'rb')
        #     self.s3.Bucket(self.bucket).put_object(Key=upload_path, Body=fp)

    def upload_object_batch(self, upload_path):
        for cur_path, dirs, files in os.walk(upload_path):
            if not files:
                continue
            for file_i in files:
                abs_file_path = os.path.join(cur_path, file_i)
                parent, f = os.path.split(upload_path)
                dest_upload_path = abs_file_path.replace(parent, '').replace('\\', '/').lstrip('/')
                print("start to upload {0} to {1}".format(abs_file_path, dest_upload_path))
                self.s3.Bucket(self.bucket).upload_file(abs_file_path, dest_upload_path)

    def bucket_exists(self, bucket_name):
        pass

    def search_one_object(self):
        pass

    def list_all_bucket(self):
        result = []
        for bucket_i in self.s3.buckets.all():
            result.append(bucket_i.name)

        return result

    @staticmethod
    def list_bucket_content(bucket_name):
        result = []
        for content_i in bucket_name.list():
            result.append({
                'name': content_i.name,
                'size ': content_i.size,
                'modified ': content_i.modified
            })

        return result

    def delete_bucket(self, del_bucket):
        self.session.delete_bucket(del_bucket)

    def download_one_file(self, obj_name, download_path):
        # with open(download_path, 'wb') as fp:
        #     self.s3.Bucket(self.bucket).Object(obj_name).download_fileobj(fp)
        self.s3.Bucket(self.bucket).Object(obj_name).download_file(download_path)

    def start_to_download_file(self, work_queues):
        try:
            while True:
                work_queue = work_queues.get(False)
                search_obj, dest_file_path = work_queue
                self.s3.Bucket(self.bucket).Object(search_obj).download_file(dest_file_path)
        except Queue.Empty:
            print("task finished.")
        except Exception as e:
            print(e)

    def download_files_batch(self, objects, download_path):
        global_queue = Queue.Queue()
        for single_obj in objects:
            if single_obj.endswith('/'):
                continue
            dest_path = os.path.dirname(os.path.join(download_path, single_obj))
            if not os.path.exists(dest_path):
                try:
                    os.makedirs(dest_path)
                except:
                    pass
            dest_file_path = os.path.join(download_path, single_obj)
            global_queue.put((single_obj, dest_file_path))
        tasks = []
        for i in range(8):
            t = threading.Thread(target=self.start_to_download_file, args=(global_queue, ))
            tasks.append(t)
        for task in tasks:
            task.start()
        for task in tasks:
            task.join()

    def delete_one_object(self, object_name):
        self.session.delete_object(
            Bucket=self.bucket,
            Key=object_name
        )

    def list_objects_by_rule(self, prefix):
        result = []
        data = self.session.list_objects_v2(
            Bucket=self.bucket,
            MaxKeys=100000,
            Prefix=prefix
        )
        for object_info in data['Contents']:
            if object_info['Key'].endswith('/'):
                continue
            result.append(object_info['Key'])
        return result

    def delete_objects_batch(self, objects):
        del_objects = []
        for object_i in objects:
            del_objects.append({
                'Key': object_i
            })
        self.session.delete_objects(
            Bucket=self.bucket,
            Delete={
                'Objects': del_objects,
                'Quiet': True
            }
        )


if __name__ == "__main__":
    access_key_id = "HbunjWK6Gxi5bldlwgEL"
    secret_access_key = "RUdbcDh6zWgqFjsQBPLxoZi7eZdhkUWNPhwmWNqL"
    _endpoint = 'snoss.xstore.ctyun.cn'
    new_s3_obj = ObjectStorageTest(_endpoint, access_key_id, secret_access_key, 'test01')
    # buckets = new_s3_obj.list_all_bucket()
    # print(buckets)

    # 上传文件
    # new_s3_obj.create_new_object('/root/storage/my_storage/_mine/README.md', 'README.md')
    # 上传目录
    # path = '/root/storage/my_storage/_mine/w8'
    # path = '/root/storage/my_storage/_mine/w11/1.2.826.0.1.3680043.2.461.11088451.1001821047'
    path = '/root/storage/my_storage/_mine/w11/pixelspacingtestimages'
    parent, d = os.path.split(path)

    import datetime
    t1 = datetime.datetime.now()
    print('{} 开始上传 .......'.format(t1))
    new_s3_obj.upload_object_batch(path)
    t2 = datetime.datetime.now()
    i = t2-t1
    print('{} 结束上传 .......\n用时 {}\n\n\n'.format(t2, i))

    ret = new_s3_obj.list_objects_by_rule(d)
    # print('上传对象: {}\n\n\n'.format(ret))

    print('等待2s开始下载')
    time.sleep(1)

    t3 = datetime.datetime.now()
    print('{} 开始下载 .......'.format(t3))
    new_s3_obj.download_files_batch(ret, './')
    t4 = datetime.datetime.now()
    j = t4-t3
    print('{} 结束下载 .......\n用时 {}\n\n\n'.format(t4, j))
