import configparser
import os
import sys
import time
import datetime

from paramiko import SSHClient


meta_path = "./"
conf = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
conf.read(meta_path)

t = datetime.datetime.now().strftime("%Y%m%d%H%M%S")


class Client(object):
    def __init__(self):
        self.ssh = None
        self.connect()

    def connect(self):
        ssh = SSHClient()
        ssh.connect(Config.client, port=22, username=Config.un, password=Config.pw)
        self.ssh = ssh

    def send(self):
        self.ssh.exec_command(Command.CMD4)


class Config(object):
    # default
    # 必须有一个及以上
    watch_service = conf.get('default', 'watch_service')
    pid = conf.get('default', 'pid')

    test_target = conf.get('default', 'test_target').split()
    # ns 或 nG 限定时间就ns，现在只能以时间为单位
    run_way = int(conf.get('default', 'run_way').replace("s", ''))
    run_time = run_way
    # ns 间隔一次统计
    interval_init = int(conf.get('default', 'interval_init').replace("s", ''))

    # cpu
    cpu_process_cnt = int(conf.get('cpu', 'process_cnt'))

    # mem
    mem_size = int(conf.get('mem', 'size'))
    mem_process_cnt = int(conf.get('mem', 'process_cnt'))
    io = int(conf.get('mem', 'io'))

    # hdd
    hdd_process_cnt = int(conf.get('hdd', 'process_cnt'))
    hdd_size = int(conf.get('hdd', 'size'))

    # net
    client = conf.get('net', 'client')
    pw = conf.get('net', 'client_password')
    un = conf.get('net', 'client_username')

    # check
    assert test_target and run_way and interval_init and client


def no_block(cmd: str):
    if '&' == cmd[-1]:
        pass
    else:
        cmd += ' &'

    return cmd


class Command(object):
    CMD1 = "iperf3 -h"
    CMD2 = "yum -y install iperf3"
    CMD3 = "iperf3 -s --logfile ./{}_iperf.log".\
        format(t)
    CMD4 = "iperf3 -c 192.168.77.100 -b 100M -t {}s".format(Config.run_time)

    CMD_STRESS_CPU = "stress -c {process_cnt} -t {time}s".\
        format(process_cnt=Config.cpu_process_cnt, time=Config.run_time)
    # 新增4个io进程，10个内存分配进程，每次分配大小1G，分配后不释放，测试100S
    CMD_STRESS_MEM = "stress –i {io} –vm {process_cnt} –vm-bytes {size} –vm-hang {sec} –t {sec}s".\
        format(io=Config.io, process_cnt=Config.mem_process_cnt, size=Config.mem_size, sec=Config.run_time)
    # 3、磁盘I/O测试 输入命令：stress –d 1 --hdd-bytes 3G 新增1个写进程，每次写3G文件块
    CMD_STRESS_HDD = "stress –d 1 --hdd-bytes {} -t {}s".format(Config.hdd_process_cnt, Config.run_time)

    CMD_STRESS_COMPLEX = "stress "

    CMD_WATCH_TOP = "top -n {} | grep {} > {}_top.log".format(Config.run_time, Config.watch_service, t)
    CMD_WATCH_TOP_ALL = "top -n {} > {}_top.log".format(Config.run_time, t)
    CMD_WATCH_DSTAT = "dstat {} {} > {}_dstat.log".\
        format(Config.interval_init, int(Config.run_time/Config.interval_init), t)
    CMD_WATCH_PIDSTAT = "pidstat -d -t -r -u -h -p {} {} {} > {}_pidstat.log".\
        format(Config.pid, Config.interval_init, int(Config.run_time/Config.interval_init), t)


class NetStress(object):
    def __init__(self):
        self.test()

    @staticmethod
    def client_send():
        c = Client()
        c.send()

    def stress(self):
        os.system(no_block(Command.CMD3))
        time.sleep(Config.interval_init)
        self.client_send()

    def test(self):
        os_ret = os.system(no_block(Command.CMD1))
        # success
        if os_ret == 0:
            pass
        else:
            # need install tools
            self.install_iperf3()

    @staticmethod
    def install_iperf3():
        cnt = 0
        success = True
        while True:
            os_ret = os.system(Command.CMD2)
            if os_ret == 0:
                break
            else:
                if cnt < 3:
                    cnt += 0
                else:
                    success = False
                    break

        if not success:
            sys.exit(-1)
        return True


class MultiStress(object):
    def __init__(self):
        pass

    @staticmethod
    def cpu():
        os.system(no_block(Command.CMD_STRESS_CPU))

    @staticmethod
    def hdd():
        os.system(no_block(Command.CMD_STRESS_HDD))

    @staticmethod
    def member():
        os.system(no_block(Command.CMD_STRESS_MEM))

    @staticmethod
    def complex():
        if "CPU" in Config.test_target:
            Command.CMD_STRESS_COMPLEX += Command.CMD_STRESS_CPU.replace("stress ", "")

        if "MEM" in Config.test_target:
            Command.CMD_STRESS_COMPLEX += Command.CMD_STRESS_MEM.replace("stress ", "")

        if "HDD" in Config.test_target:
            Command.CMD_STRESS_COMPLEX += Command.CMD_STRESS_HDD.replace("stress ", "")
        ret = os.system(no_block(Command.CMD_STRESS_COMPLEX))
        print(no_block(Command.CMD_STRESS_COMPLEX))
        if not ret:
            raise Exception("STRESS ERROR")


class Controller(object):
    def __init__(self):
        self.init()

    @staticmethod
    def multi():
        ls = [i for i in Config.test_target if i != 'NET']
        if len(ls):
            mul = MultiStress()
            if len(ls) == 1:
                if 'CPU' in ls:
                    mul.cpu()
                elif "MEM" in ls:
                    mul.member()
                elif "HDD" in ls:
                    mul.hdd()
                else:
                    print('CONFIG ERROR')
            else:
                mul.complex()
        else:
            pass

    def init(self):
        if 'NET' in Config.test_target:
            assert isinstance(Config.test_target, list)
            n = NetStress()
            n.stress()

        self.multi()

        print("watch: <<<<<<<<<< ")

    @staticmethod
    def watch():
        if Config.watch_service:
            os.system(no_block(Command.CMD_WATCH_DSTAT))
            os.system(no_block(Command.CMD_WATCH_TOP))
            os.system(no_block(Command.CMD_WATCH_PIDSTAT))
        else:
            os.system(no_block(Command.CMD_WATCH_TOP_ALL))
            os.system(no_block(Command.CMD_WATCH_DSTAT))

    def install(self):
        pass


if __name__ == '__main__':
    pass
