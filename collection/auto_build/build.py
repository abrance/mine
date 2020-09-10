import configparser
import os

from init import ASMRewrite
from install import StandardInstall, ASMInstall
from utils import check_ret, conf_method_dc, exe_dc, sgw_build
from virtual_install import Virtualenv


class ProPull(object):
    """
    获得的参数需要自己进行处理
    """

    def __init__(self, setting, globe_info):
        try:
            self.state = None
            self.sec_name = None
            self.pros_name = None
            self.build_path = None
            self.abs_path = None
            self.version = None
            self.setting = setting
            self.globe_info = globe_info
            self.username = None
            self.password = None
            self.url = None
            self.web_app = None
            self.web_app_url = None
            self.pro_path = None        # 项目真实路径
            self.fill()

            self.run()
        except Exception as e:
            print(e)
            print('no pull')

    def fill(self):
        self.state = self.setting.get('svn', True)
        self.build_path = self.globe_info.get('build_path')
        self.version = self.globe_info.get('version')
        self.username = self.globe_info.get('svn_user')
        self.password = self.globe_info.get('svn_password')

        self.sec_name = self.setting.get('name')
        self.url = self.setting.get('url')
        if not self.url:
            raise Exception
        self.pros_name = str(self.url).split('/')[-1]
        if self.state == 'off':
            raise Exception
        else:
            self.state = True
        self.web_app = self.setting.get('web_app', '')
        self.web_app_url = self.setting.get('web_app_url', '')

    def co(self):
        # pro_path = self.build_path + '/' + self.version + '/' + self.sec_name + '/' + self.pros_name
        sec_dir = '/'.join((self.build_path, self.version, self.sec_name))
        if not os.path.exists(sec_dir):
            os.system('mkdir -p {}'.format(sec_dir))
        pro_path = '/'.join((self.build_path, self.version, self.sec_name, self.pros_name))
        self.pro_path = pro_path

        # 2020/9/4 如果已存在项目名，将之前的项目名打包
        if os.path.exists(pro_path):
            new_pro_name = ''
            for i in range(100):
                new_pro_name = '_'.join((pro_path, str(i + 1)))
                if os.path.exists(new_pro_name):
                    pass
                else:
                    break
            os.system('mv {} {}'.format(pro_path, new_pro_name))

        ret1 = os.system('svn co {} {} --username {} --password {}'.
                         format(self.url, pro_path, self.username, self.password))
        _ret1 = check_ret(ret1)
        if _ret1:
            print('<<<< SUCCESS svn co {}'.format(self.url))

            # 2020/9/7 如果是web应用，需要checkout前端代码
            if self.web_app:
                web_path = pro_path + '/' + 'webapp'
                if not os.path.exists(web_path):
                    os.system('mkdir -p {}'.format(web_path))
                ret2 = os.system('svn co {} . {} --username {} --password {}'.
                                 format(self.web_app_url, web_path, self.username, self.password))
                _ret2 = check_ret(ret2)
                if ret2:
                    print('<<<< SUCCESS svn co {}'.format(self.web_app_url))
                else:
                    print('<<<< FAIL svn co {}'.format(self.web_app_url))
                    return False

            return True
        else:
            print('<<<< FAIL svn co {}'.format(self.url))
            return False

    def run(self) -> None:
        if self.state:
            self.co()
        else:
            print('state {}'.format(self.state))


class LoadConfig(object):
    def __init__(self, conf_path):
        self.conf_path = conf_path
        self.conf = None
        self.globe = None
        self.asm = None
        self.get_conf()
        self.conf_path_dc = dict()
        self.get_conf_path()

    def get_conf(self):
        self.read_conf()

    def read_conf(self):
        if os.path.exists(self.conf_path):
            self.conf = dict()
            self.globe = dict()
            self.asm = dict()
            # 2020/8/22 读取配置
            conf = configparser.ConfigParser()
            conf.read(self.conf_path)
            sections = conf.sections()
            # all_options = [conf.options(sec) for sec in sections]
            # 2020/8/22 sec: cli mds
            # module_info: {'name': 'cli', 'options': ['port', 'region'], 'items': {'port': '5000', 'region': '2020'}}

            # 2020/9/4 全局和其它模块分离，asm也分离出来，因为部署和其它不同
            for sec in sections:
                # module_info = {
                #     'name': sec,
                #     'options': conf.options(sec),
                #     'items': dict(conf.items(sec))
                # }
                # self.conf.__setitem__(sec, module_info)
                if sec == 'global':
                    self.globe = dict(conf.items(sec))
                elif sec == 'asm':
                    self.asm = dict(conf.items(sec))
                    self.asm['name'] = sec
                else:
                    self.conf.__setitem__(sec, dict(conf.items(sec)))
                    self.conf[sec]['name'] = sec
        else:
            print('conf no found')
            pass

    @staticmethod
    def module_rule():
        # 2020/9/4 各个模块匹配 配置文件路径 规则
        dc = dict()
        dc['cli'] = ['transfer_client' + '/' + 'conf' + '/' + 'config.ini',
                     'transfer_client' + '/' + 'conf' + '/' + 'dconfig.ini']
        dc['fpt'] = 'config.ini'
        dc['mds'] = 'meta.ini'
        dc['monitor'] = 'monitor.ini'
        dc['sdm'] = 'meta.ini'
        # dc['sgw'] = 'src/sgw'

        return dc

    def get_conf_path(self):
        # 2020/9/4 加载各个模块的配置路径
        for module, v in self.conf.items():
            module_info = v
            svn = module_info.get('svn')
            if svn == 'off':
                pro_dir_name = module_info.get('pro_dir_name')
            else:
                build_path = self.globe.get('build_path')
                version = self.globe.get('version')
                pro_name = module_info.get('url').split('/')[-1]
                pro_dir_name = '/'.join((build_path, version, module, pro_name))

            _path = self.module_rule().get(module)
            if type(_path) is str:
                config_path = pro_dir_name + '/' + self.module_rule().get(module)
            elif type(_path) is list:
                config_path = [pro_dir_name + '/' + i for i in _path]
            elif module in ('sgw', 'system'):
                continue
            else:
                print('typeerror module: {}'.format(module))
                return False

            self.conf_path_dc.__setitem__(module, config_path)

    def input(self):
        pass

    def auto_conf(self):
        pass


class ProLoadConfig(LoadConfig):
    conf_path = 'conf.ini'

    def __init__(self):
        super(ProLoadConfig, self).__init__(self.conf_path)


class ASMPull(ProPull):
    def __init__(self, setting, globe_info, host):
        self.host = host
        super(ASMPull, self).__init__(setting, globe_info)

    def fill(self):
        super(ASMPull, self).fill()
        self.sec_name = self.host

    def co(self):
        super(ASMPull, self).co()
        # 2020/9/7 这里顺便把asm配置了，不然再找到asm的地址麻烦
        info = {
            'conf_path': self.pro_path,
            'module_name': self.host,
            'role_id': '{}_id'.format(self.host),
            'ip': '{}_asm_ip'.format(self.host),
            'port': '{}_asm_port'.format(self.host),
            'rest_port': '{}_asm_rest_port'.format(self.host),
        }
        print('asm_info: {}'.format(info))
        ASMRewrite(info)


class ProInit(object):
    """
    提供控制的功能
    """
    def __init__(self, module: str, settings_dc):
        self.module_name = module
        self.pro_location = None
        settings = settings_dc
        conf = settings.conf
        print('\n\nconf:{}\n\n'.format(conf))
        asm = settings.asm
        globe_info = settings.globe

        info = conf.get(module)

        # 2020/9/9 如果想不拉代码只修改配置，就注释这一行
        p = ProPull(info, globe_info)
        if module == 'system':
            settings.system = p.pro_path
        else:
            self.pro_location = p.pro_path

            # if module == 'cli':
            #     self.pro_location = self.pro_location
            v = Virtualenv()

            if module != 'sgw':
                config_path = settings.conf_path_dc.get(module)
                print('\nsettings.conf_path_dc: {}'.format(settings.conf_path_dc))
                method = conf_method_dc.get(module)
                if method:
                    # 2020/9/9 进行配置文件
                    method(config_path, globe_info)
            else:
                # 2020/9/9 sgw需要进行单独的配置
                pass

            # 2020/9/8 monitor sdm 不依赖 asm
            # 2020/9/9 如果不使用asm就加入这里
            if module not in ('monitor', 'sdm'):
                a = ASMPull(asm, globe_info, module)
                _info = {
                    'installer_path': settings.system,
                    'pro_dir': a.pro_path,
                    'exe_cmd': '{} {}'.format(v.get_interpret('asm', a.pro_path), a.pro_path+'/'+'asm_main')
                }
                print('_info: {}'.format(_info))
                ASMInstall(module, _info)
                # 2020/9/10 需要在这里配置asm 加入systemd

            # 2020/9/9 进行 加入systemd
            interpret = v.get_interpret(module, self.pro_location)
            if module != 'sdm':
                info_dc = dict()
                info_dc['pro_dir'] = self.pro_location
                info_dc['installer_path'] = settings.system
                info_dc['exe_cmd'] = '{} {}'.format(interpret, exe_dc.get(module))
                if module == 'sgw':
                    info_dc['exe_cmd'] = exe_dc.get(module).format(
                        globe_info.get('region_id'), globe_info.get('sgw_listen'),
                        globe_info.get('sgw_asm_ip'), globe_info.get('sgw_listen'),
                        globe_info.get('sgw_asm_ip'), globe_info.get('sgw_asm_port'),
                        globe_info.get('sgw_upload_path')
                    )
                    # 2020/9/9 sgw需要先编译
                    build_path = self.pro_location+'/'+'build'
                    ret = sgw_build(build_path)
                    if not ret:
                        print('sgw_build FAIL: {}'.format(build_path))
                StandardInstall(module, info_dc)


class SystemInit(object):
    def __init__(self):
        settings = ProLoadConfig()
        conf = settings.conf
        print('conf_path_dc: {}'.format(settings.conf_path_dc))
        if not settings.conf_path_dc:
            raise

        for module in conf.keys():
            ProInit(module, settings)


if __name__ == '__main__':
    SystemInit()
    # settings = ProLoadConfig()
    # print('conf: {}\nasm: {}\nglobe: {}'.format(settings.conf, settings.asm, settings.globe))
