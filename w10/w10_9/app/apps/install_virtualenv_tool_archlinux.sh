#! /bin/bash

echo 'install virtualenv tool ....'
pip3 install virtualenv -i https://pypi.tuna.tsinghua.edu.cn/simple
pip3 install virtualenvwrapper -i https://pypi.tuna.tsinghua.edu.cn/simple
mkdir ~/py_vm
echo "export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3" >> ~/.bashrc
echo "export WORKON_HOME=~/py_vm" >> ~/.bashrc
echo "source /home/imba/.local/bin/virtualenvwrapper.sh" >> ~/.bashrc
source ~/.bashrc 
