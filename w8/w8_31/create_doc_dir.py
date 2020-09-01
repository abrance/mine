import random
import shutil
import sys
import os

c = y = s = f = 0
# 2020/9/1 分别表示 case_no, year, store_year, store_time(years) 的个数
factor_dc = {
    'c': c,
    'y': y,
    's': s,
    'f': f,
    'e': []
}


def parse(args_ls):
    try:
        for arg in args_ls:
            op, value = arg.split('=')
            if op in factor_dc.keys():
                factor_dc[op] = int(value)
            else:
                factor_dc['e'].append(op)
        return factor_dc
    except Exception as e:
        print(e)
        return False


def _mkdir(p_dir, k, cnt):
    dc = {
        'c': '{}'.format(300+cnt),
        'y': '{}'.format(1990+cnt),
        's': '{}'.format(random.choice((0, 30, -1))),
        'f': 'test-{}.pdf'.format(cnt+1)
    }
    if k in dc.keys():
        v = dc[k]

        for i in range(cnt):
            dir_name = v
            __dir = '/'.join((p_dir, dir_name))
            if os.path.exists(__dir):
                shutil.rmtree(__dir)
            os.mkdir(__dir)
        return True
    else:
        return False


def mk_tree(__c, __y, __s, __f, __e, kwargs):
    # 2020/9/1 组装成一个目录树
    pwd = os.path.abspath('./')
    ret = _mkdir(pwd, 'c', __c)
    if ret:
        _mkdir()


def mkdir(f_dc: dict):
    _c, _y, _s, _f, _e = f_dc.get('c'), f_dc.get('y'), f_dc.get('s'), f_dc.get('f'), f_dc.get('e')
    kwargs = {}
    if _e:
        try:
            # 2020/9/1 处理 其它参数逻辑， 保证良好扩展性
            for item in _e:
                if str(item).startswith('more_level'):
                    k, v = item.split('=')
                    kwargs.__setitem__(k, v)

            mk_tree(_c, _y, _s, _f, _e, kwargs)
        except Exception as e:
            print(e)
            return False


def mk_file():
    pass


def mk_dir_files():
    pass


kw_dc = {
    'mkdir': mkdir,
    'files': mk_file,
    'mkdir_files': mk_dir_files
}


def _input():
    args = sys.argv[1:]
    keyword = sys.argv[1]  # 2020/8/31 关键字

    factors = args[1:]  # 2020/8/31 其它的因子
    func = kw_dc.get(keyword)
    parse(factors)
    if func:
        func(factor_dc)
    else:
        print('* ERROR * ' * 10)
        sys.exit(-1)


if __name__ == '__main__':
    _input()
