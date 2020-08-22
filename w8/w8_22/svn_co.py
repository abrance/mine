import os
import sys
from enum import Enum
from threading import Thread


class DcInfo(Enum):
    mds_info = {}
    agent_info = {}
    sgw_info = {}
    fpt_info = {}
    monitor_info = {}


class SvnCopy(Thread):
    """
    key: MDS, AGENT, SGW, FPT, MONITOR
    """

    dc = {
        'mds': mds_info,
        'agent': agent_info,
        'sgw': sgw_info,
        'fpt': fpt_info,
        'monitor': monitor_info
    }

    def __init__(self, key):
        super(SvnCopy, self).__init__()
        self.key = key
        self.info = None
        self.get_info()

    def get_info(self):
        self.info = self.dc.get(self.key)

    @staticmethod
    def check_ret(ret):
        # 2020/8/20 返回值为0才是正常
        if ret:
            return False
        else:
            return True

    def svn_co(self, url):
        ret1 = os.system('svn co {}'.format(url))
        _ret1 = self.check_ret(ret1)
        if _ret1:
            print('<<<< success svn co {}'.format(url))
            return True
        else:
            print('<<<< FAIL svn co {}'.format(url))
            return False

    def add_job(self):
        pass

    def run(self) -> None:
        self.add_job()


def svn():
    ASM = 'http://192.168.80.200:8080/svn/bigstorage/trunk/archivesStorage/asm_server'
    AGENT = 'http://192.168.80.200:8080/svn/bigstorage/trunk/archivesStorage/档案2.0版本/medical_client_archives_windows'
    MDS = 'http://192.168.80.200:8080/svn/bigstorage/trunk/archivesStorage/档案2.0版本/metadata_server_archives_v2'

    ret = os.system('git pull')
    if ret:
        print('\ngit pull error\n')
        sys.exit(1)
    else:
        return ret
