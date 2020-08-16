
-- 创建用户 metadata，密码是 anyun100
CREATE USER 'metadata'@'localhost' identified by 'anyun100';

-- 创建数据库，存在则不创建
CREATE DATABASE IF NOT EXISTS metadata8 CHARACTER SET utf8mb4;

-- 将数据库 metadata 的所有权限都授权给用户 metadata
GRANT ALL ON metadata8.* to 'metadata'@'localhost';
GRANT ALL ON metadata8.* to 'metadata'@'%';

-- 允许 metadata 用户远程登录
GRANT ALL PRIVILEGES ON metadata8.* to 'metadata'@'%' IDENTIFIED BY 'anyun100' WITH GRANT OPTION;
FLUSH PRIVILEGES;
