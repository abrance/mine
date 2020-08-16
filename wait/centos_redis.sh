wget http://download.redis.io/releases/redis-5.0.2.tar.gz
tar -zxvf redis-5.0.2.tar.gz
yum install gcc
cd redis-5.0.2
make MALLOC=libc
cd src && make install
redis-server -v
systemctl status redis
whereis redis.conf
sed -i "s/bind 127.0.0.1/# bind 127.0.0.1/g" 
