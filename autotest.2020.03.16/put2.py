# -*- coding: utf-8 -*-

# 多线程上传文件

# mike
# 2019-12-10

import protocol

def upload_entry(sgw_addr, sgw_port, nr_files, nr_threads, self_tid):
    n = self_tid
    while n < nr_files:
        p = protocol.Protocol(sgw_addr, sgw_port)
        p.launch()
        filepath = "{:016d}".format(n)
        p.putfile1(filepath)
        p.finish()
        n += nr_threads

def download_entry(sgw_addr, sgw_port, nr_files, nr_threads, self_tid):
    n = self_tid
    while n < nr_files:
        p = protocol.Protocol(sgw_addr, sgw_port)
        p.launch()
        filepath = "{:016d}".format(n)
        rc = p.getfile1(filepath)
        if rc:
            pass
        else:
            print("file {} download failed!".format(filepath))
        p.finish()
        n += nr_threads

def run_threads(sgw_addr, sgw_port, nr_files, nr_threads, thread_entry):
    import threading
    threads = list()
    for i in range(nr_threads):
        t = threading.Thread(
            target=thread_entry,
            args=(sgw_addr, sgw_port, nr_files, nr_threads, i)
        )
        threads.append(t)
    for t in threads:
        t.start()
    for t in threads:
        t.join()

def main(sgw_addr, sgw_port, nr_files, nr_threads):
    import subprocess
    rc = subprocess.call(
        ["./testfile", "-G", "-s256KB", "-n{}".format(nr_files)]
    )
    if rc == 0:
        # 上传文件
        run_threads(sgw_addr, sgw_port, nr_files, nr_threads, upload_entry)
        run_threads(sgw_addr, sgw_port, nr_files, nr_threads, download_entry)
    else:
        print("generate files failed!")
        sys.exit(-1)

if __name__ == '__main__':
    import sys

    argc = len(sys.argv)
    if argc == 5:
        sgw_addr = sys.argv[1]
        sgw_port = int(sys.argv[2])
        nr_files = int(sys.argv[3])
        nr_threads = int(sys.argv[4])
    else:
        print("usage: {} sgw_ipv4 sgw_port nr_files nr_threads".format(sys.argv[0]))
        sys.exit(-1)

    try:
        main(sgw_addr, sgw_port, nr_files, nr_threads)
    except KeyboardInterrupt:
        sys.exit(-1)
