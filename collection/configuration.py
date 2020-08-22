import configparser

conf_path = './conf.ini'

conf_info = dict()
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
    conf_info.__setitem__(sec, module_info)
