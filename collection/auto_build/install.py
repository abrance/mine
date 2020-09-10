import os

from configobj import ConfigObj

from utils import check_ret


class BaseInstall(object):
    def __init__(self, module, info):
        self.install_prefix = ''
        self.module = module                    # 宿主模块名
        self.info = info

        self.installer_path = None              # systemd 根目录绝对路径
        self.install_name = None                # 对应模块名字
        self.service_filename = None            # service文件绝对路径
        self.config = None                      # configobj对象
        self.fill()
        self.write()

    def fill(self):

        self.installer_path = self.info.get('installer_path')
        self.get_install_prefix()
        self.install_name = '{}{}'.format(self.install_prefix, self.module)
        self.get_service_filename()
        if not os.path.exists(self.service_filename):
            print('service_filename: {} no exist'.format(self.service_filename))
            return False
        self.get_config_obj()

    def get_install_prefix(self):
        # 2020/9/9 子类须重写此方法
        pass

    def get_service_filename(self):
        # 2020/9/9 子类须重写
        pass

    def get_config_obj(self):
        self.config = ConfigObj(self.service_filename)

    def write(self):
        pass

    def install(self):
        _ret = os.system('sh {}'.format(os.path.join(os.path.dirname(self.service_filename), 'install.sh')))
        ret = check_ret(_ret)
        return ret


class StandardInstall(BaseInstall):
    def __init__(self, module, info):
        super(StandardInstall, self).__init__(module, info)

    def get_install_prefix(self):
        self.install_prefix = 'systemd_for_'

    def get_service_filename(self):
        if self.module == 'monitor':
            self.service_filename = os.path.join(self.installer_path,
                                                 self.install_name, '{}.service'.format(self.module))
        else:
            self.service_filename = os.path.join(self.installer_path,
                                                 self.install_name, 'new-{}.service'.format(self.module))

    def write(self):
        op = self.config['Service']

        op['WorkingDirectory'] = self.info.get('pro_dir')
        op['ExecStart'] = self.info.get('exe_cmd')
        self.config.write()
        self.install()


class ASMInstall(BaseInstall):
    def __init__(self, module, info):
        super(ASMInstall, self).__init__(module, info)

    def get_install_prefix(self):
        self.install_prefix = 'systemd_for_asm_'

    def get_service_filename(self):
        print('<<< install_name: {}'.format(self.install_name))

        self.service_filename = os.path.join(self.installer_path,
                                             self.install_name, 'new-asm-{}.service'.format(self.module))

    def write(self):
        op = self.config['Service']

        op['WorkingDirectory'] = self.info.get('pro_dir')
        op['ExecStart'] = self.info.get('exe_cmd')
        self.config.write()
        self.install()
