#!/bin/bash
source /usr/local/bin/virtualenvwrapper.sh
mkvirtualenv asm -p python2 && pip install --upgrade pip -i https://pypi.mirrors.ustc.edu.cn/simple/ && pip install -r $1 -i https://pypi.mirrors.ustc.edu.cn/simple/