-- 创建表结构
-- 2020-3-18

-- version 1.0 文件信息表中含user_id，而且不能为空，这样需要注册才能上传文件

-- 文件信息表， fields：file_id, user_id, agent_id, dirpath, fname, fmd5, fsize, create_time, last_mod, state, level1_t1, ..., level1_t8, level2_t1, level_t32,

create table file_index (
       file_id int(10) unsigned primary key auto_increment not null,
       user_id int(10) unsigned not null,
       agent_id SMALLINT DEFAULT -1,
       dirpath varchar(64) not null,
       fname varchar(32) not null,
       fmd5 varchar(64) not null,
       fsize int(10) unsigned not null,
       create_time DATETIME DEFAULT '9999-12-31 23:59:59',
       last_mod DATETIME,
       state int(1) unsigned not null,
       level1_t1 varchar(32),
--todo       
)








