import os

from init import CliRewrite, FPTRewrite, MDSRewrite, MonitorRewrite, SDMRewrite


def check_ret(ret):
    print('<<<< check_ret  ret:{} '.format(ret))
    # 2020/8/20 返回值为0才是正常 检查os.system的执行状态
    if ret:
        print('os execute ERROR')
        return False
    else:
        return True


def sgw_build(build_path):
    print('<<<< sgw_build build_path: {}'.format(build_path))
    _ret = os.system('sh ./sgw_make.sh {}'.format(build_path))
    return check_ret(_ret)


conf_method_dc = {
    'cli': CliRewrite,
    'fpt': FPTRewrite,
    'mds': MDSRewrite,
    'monitor': MonitorRewrite,
    'sdm': SDMRewrite,
}

exe_dc = {
    'cli': '/transfer_client/agent.py',
    'mds': '/app/main',
    'fpt': 'main.py',
    'sgw': '/bin/sgw w -r {} -s 1 -g 1 -l 0.0.0.0:{}:0x90000001 -c '
           '{}:{} -a {}:{} -b {} -w 16 -d',
    'monitor': 'main.py',
    'asm': 'asm_main'
}
