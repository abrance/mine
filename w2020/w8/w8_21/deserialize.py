# @Time    : 2020/8/21 11:27
# @Author  : DaguguJ
# @Email   : 1103098607@qq.com
# @File    : deserialize.py
import ast
from itsdangerous import URLSafeSerializer


def deserialize(file_hash):
    # key = current_app.config.get("SECRET_KEY", "The secret key is secret")
    key = "secret key is secret"
    try:
        s = URLSafeSerializer(key)
        file_info_str, = s.loads(file_hash)
        file_info_dict = ast.literal_eval(file_info_str)
        return file_info_dict
    except Exception as e:
        print(str(e))
        return {}


if __name__ == '__main__':
    ha = '.eJyLVqpWT8vMSY3PS8xNVbdSUH_auuJl84rnqxe86GpSMDAwVHg2fduzuUtf7J_wYu8avZKKEnUdBYiO3BRTkAYLAzMDcxODVEPjVANjY1PDJIPU5GSjNEvTFAvL5LQkC5D6otT0zPy8-MwUoAYjA0NLoFBJZm5qcUlibgHIDCMDIwNdAwtdQ0sFQ2MrU1MrAyO4NQWJJRkgNYYGBgb6Rfn5JfogEX1DI2MIUq9VigUANc9Alw.fpD13pdKwapnEHI_ZkoBeqy_0Ek'
    a = deserialize(ha)
    print(a)
