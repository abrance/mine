import configparser
import os

from configobj import ConfigObj

conf_path = './conf.ini'

# 2020/8/22 写入配置类
config = ConfigObj(conf_path)

AGENT_INFO = {}
MDS_INFO = {}
FPT_INFO = {}
SGW_INFO = {}
MONITOR_INFO = {}
ASM_INFO = {}


class LoadConfig(object):
    def __init__(self):
        self.conf = None

    def get_conf(self):
        self.read_conf()

    def read_conf(self):
        if os.path.exists(conf_path):
            self.conf = dict()
            # 2020/8/22 读取配置
            conf = configparser.ConfigParser()
            conf.read(conf_path)
            sections = conf.sections()
            all_options = [conf.options(sec) for sec in sections]
            # 2020/8/22 sec: agent mds
            # module_info: {'name': 'agent', 'options': ['port', 'region'], 'items': {'port': '5000', 'region': '2020'}}
            for sec in sections:
                module_info = {
                    'name': sec,
                    'options': conf.options(sec),
                    'items': dict(conf.items(sec))
                }
                self.conf.__setitem__(sec, module_info)
        else:
            print('conf no found')
            pass

    def input(self):
        pass

    def auto_conf(self):
        pass


if __name__ == '__main__':
    pass
