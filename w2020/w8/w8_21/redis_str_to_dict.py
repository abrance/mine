# @Time    : 2020/8/21 13:38
# @Author  : DaguguJ
# @Email   : 1103098607@qq.com
# @File    : redis_str_to_dict.py
import json
from pprint import pprint

str1 = "{'\xe6\xa0\x87\xe7\xad\xbe\xe5\x90\x8d': ''}"


def str_to_dict(dc_str: str) -> dict:
    # 2020/8/21 将字符表示的字典转为字典类型
    dc_str = dc_str.replace('{', '')
    dc_str = dc_str.replace('}', '')

    items_str = dc_str.split(',')
    dc = dict()
    try:
        for item in items_str:
            k, v = item.split(':')
            k = str(k).strip(' ')
            v = str(v).strip(' ')
            k = k.replace('\'', '')
            k = k.replace('\"', '')
            v = v.replace('\'', '')
            v = v.replace('\"', '')
            k = unicode_to_str(k)
            dc.__setitem__(k, v)
        return dc

    except Exception as e:
        print(e)
        return {}


def unicode_to_str(uni_str: str) -> str:
    # 2020/8/21 将/x开头的 unicode编码转为 正常编码的字符串， 相当于字符前面加了b
    return uni_str.encode('ISO-8859-1').decode()


if __name__ == '__main__':
    info = str_to_dict(str1)
    print(info)
    var = info.get('标签名')
    print('v: {}'.format(var))
