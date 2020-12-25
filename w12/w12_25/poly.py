# -*- coding: utf-8 -*-
"""
ploy
"""

import lzma
import os
import sys


def ncd(input_file, output_file):
    x = open(input_file, 'rb').read()  # file 1 of any type
    y = open(output_file, 'rb').read()  # file 2 of the same type as file 1
    x_y = x + y  # the concatenation of files

    x_comp = lzma.compress(x)  # compress file 1
    y_comp = lzma.compress(y)  # compress file 2
    x_y_comp = lzma.compress(x_y)  # compress file concatenated

    # print len() of each file
    print(len(x_comp), len(y_comp), len(x_y_comp), sep=' ', end='\n')

    # magic happens here
    _ncd = (len(x_y_comp) - min(len(x_comp), len(y_comp))) / max(len(x_comp), len(y_comp))

    print(_ncd)
    return _ncd


def poly(_path, _outputs_path):
    with open(_path, 'r') as f:
        # 压缩算法
        import bz2
        text = f.read()
        cmp_src = bz2.compress(text.encode('utf-8'))  # bz2 实现压缩，也可手动实现

        with open(_outputs_path, 'w') as output_file:
            output_file.write(cmp_src)
    return True


def get_paths():
    _input_path = sys.argv[0].strip()
    _outputs_path = ''

    if len(sys.argv) == 1:
        # path = sys.argv[0].strip()
        pass
    elif len(sys.argv) == 2:
        _outputs_path = sys.argv[1]
    else:
        pass

    assert os.path.exists(_input_path)
    if not _outputs_path:
        _, filename = os.path.split(_input_path)
        fr, ext = os.path.splitext(filename)
        _outputs_path = os.path.join(_, fr + '_out.{}'.format(ext))
    return _input_path, _outputs_path


# program entry
if __name__ == "__main__":
    input_path, output_path = get_paths()  # get foo

    result = poly(input_path, output_path)
    print("Polymorphic file:{} -> {} successfully".format(input_path, output_path))

    # test ncd of two files
    ret = ncd(input_path, output_path)
    assert ret > 0.7
