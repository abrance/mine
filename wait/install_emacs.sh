yum -y install libxpm-devel
xz -d emacs-26.3.tar.xz
tar -xvf emacs-26.3.tar
cd emacs-26.3
yum -y install ncurses-devel libXpm-devel libjpeg-turbo-devel openjpeg-devel openjpeg2-devel turbojpeg-devel giflib-devel libtiff-devel gnutls-devel libxml2-devel GConf2-devel dbus-devel wxGTK-devel gtk3-devel libselinux-devel gpm-devel librsvg2-devel ImageMagick-devel
./configure --with-pop --with-mailutils
make && make install
