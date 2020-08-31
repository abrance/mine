import sys
import os


factor_dc = {
    ''
}


def parse(args_ls):
    for arg in args_ls:
        pass


def _mkdir(dir_name, case_no):
    # 2020/8/31 dir_name 已存在，case_no 未存在


def mkdir(case_cnt: int):
    parse()

    _dir = os.path.abspath('./')
    cnt = 0
    for i in range(100):
        case_no = '30{}'.format(i)
        __dir = '/'.join((_dir, case_no))
        if os.path.exists(__dir):
            pass
        else:
            os.mkdir(__dir)

        cnt += 1
        if cnt == case_cnt:
            break


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
    keyword = sys.argv[1]       # 2020/8/31 关键字

    factors = args[1:]          # 2020/8/31 其它的因子
    func = kw_dc.get(keyword)
    if func:
        func(factors)
    else:
        print('* ERROR * '*10)
        sys.exit(-1)



if __name__ == '__main__':
    _input()
