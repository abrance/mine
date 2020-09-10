#! /bin/bash
echo 'install virtualenv tool ....'
pip3 install virtualenv
pip3 install virtualenvwrapper
mkdir ~/py_vm
echo "export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3" >> ~/.bashrc
echo "export WORKON_HOME=~/py_vm" >> ~/.bashrc 
echo "source /usr/local/bin/virtualenvwrapper.sh" >> ~/.bashrc 
source ~/.bashrc
