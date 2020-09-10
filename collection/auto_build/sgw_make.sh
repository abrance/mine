yum install cmake3 -y
yum install openssl-devel -y

#cmake3 .. -DMD5=ON
#cmake3 .. -DMD5=OFF
#cmake3 ..

cd $1 && make
