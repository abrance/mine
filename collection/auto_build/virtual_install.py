import os

from utils import check_ret


class Virtualenv(object):
    def __init__(self):
        self.vm = self.check_vir_env()
        if not self.vm:
            raise

    @staticmethod
    def check_vir_env():
        with open('/root/.bashrc') as file:
            for line in file.readlines():
                if 'WORKON_HOME' in line:
                    vm_path = line.split('=')[-1].replace('\n', '').replace('~', '/root', 1)
                    return vm_path
            # 2020/9/9 如果没有这一行，就说明没安装虚拟环境，直接运行安装virtualen的脚本
            _ret = os.system('sh ./install_virtualenv_tool.sh')
            ret = check_ret(_ret)
            if ret:
                return '/root/py_vm'
            else:
                return False

    @staticmethod
    def pip_install(module, requirements):
        print('<<<< pip_install module: {} requirements: {} '.format(module, requirements))
        cmd = 'sh ./{}.sh {}'.format(module, requirements)
        print('cmd: {}'.format(cmd))
        _ret = os.system(cmd)
        ret = check_ret(_ret)
        return ret

    def get_interpret(self, module, pro_path):
        # 2020/9/9 安装对应模块的虚拟环境
        requirements = self.get_requirement(pro_path)
        print('vm:{} module:{}'.format(self.vm, module))
        if os.path.exists(self.vm + '/' + module):
            pass
        else:
            ret = self.pip_install(module, requirements)
            if ret:
                print('pip install SUCCESS')
                return '{}/{}/bin/python'.format(self.vm, module)
            else:
                print('pip install FAIL')
                return False

    @staticmethod
    def get_requirement(pro_path):
        return pro_path + '/' + 'requirements.txt'
