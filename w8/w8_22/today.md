# 安装archlinux

## 经验
    U盘制作软件选用Etcher，直接选择iso文件，flash即可
    需要先挂载根目录，再挂载efi目录

## 坑
    当使用wifi的时候，需要查阅安装networkmanager 服务单元
    pacman -Qql networkmanager | grep systemd
    
    