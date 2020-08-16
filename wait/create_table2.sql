-- 创建表结构
--
-- 档案存储系统和医疗存储系统使用同一套表结构
--
-- 2020-03-20

-- 文件信息表
--
-- 这个表一行数据需要的空间：
-- 8+4+32+3840+32+256+4+4+10+4+32+2+8+8+8+8+80=4340，考虑容错增大一倍
-- 为 8192。
--
-- 8192*1000万=8192*10MB=81920MB=82GB
-- 8192*5000万=8192*50MB=409600MB=410GB
-- 8192*1亿=8192*100MB=819200MB=820GB
-- 8192*5亿=8192*500MB=4096000MB=4096GB=4TB
--
-- 单个主键索引的大小：8+4+32=44
--
-- 44*1000万=44*10MB=440MB
-- 44*5000万=44*50MB=2200MB=2.2GB
-- 44*1亿=44*100MB=4400MB=4.4GB
-- 44*5亿=44*500MB=22000MB=22GB
--
-- 在高性能的服务器中，22GB 的索引是完全可以放到内存中的。

CREATE TABLE `fileinfo1` (
       create_time DATETIME NOT NULL,    -- 文件创建时间，以这个作为分区
       agentid INT NOT NULL,             -- 客户端标识
       fileid CHAR(32) NOT NULL, -- md5(agentid+dirpath+filename)

       dirpath TEXT(3840) NOT NULL, -- 文件所在的目录路径，CHAR 最大只能是 255
       dirid CHAR(32) NOT NULL, -- md5(dirpath)，在此建立索引，主要是想缩小索引大小
       filename CHAR(255) NOT NULL, -- 文件名

       fileclass INT DEFAULT 0,     -- 文件分类：图片，文本，doc，excel……
       business_type INT DEFAULT 0, -- 业务类型：档案，医疗
       filesuffix CHAR(10) DEFAULT NULL, -- 后缀名
       filetype INT DEFAULT 0,      -- JPG, PNG, TXT, MD……文件可能没有后缀名，但还是有类型
       filemd5 CHAR(32) NOT NULL,   -- 文件 md5 散列值
       filestate TINYINT DEFAULT 0, -- 文件状态
       filesize BIGINT DEFAULT 0,   -- 文件大小

       delete_time DATETIME DEFAULT '9999-12-31 23:59:59', -- 文件被删除时间
       last_access_time DATETIME DEFAULT '1970-01-01 00:00:00', -- 文件最后访问时间
       last_modify_time DATETIME DEFAULT '1970-01-01 00:00:00', -- 文件最后修改时间

       -- tag1 ~ tag8: 一级编目，tag 的具体含义要到具体的编目表中查找
       tag1 CHAR(10) DEFAULT NULL,
       tag2 CHAR(10) DEFAULT NULL,
       tag3 CHAR(10) DEFAULT NULL,
       tag4 CHAR(10) DEFAULT NULL,
       tag5 CHAR(10) DEFAULT NULL,
       tag6 CHAR(10) DEFAULT NULL,
       tag7 CHAR(10) DEFAULT NULL,
       tag8 CHAR(10) DEFAULT NULL,

       PRIMARY KEY (`create_time`, `fileid`, `agentid`),
       INDEX `i_index1` (`dirid`)
)
ENGINE=InnoDB
DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_bin
PARTITION BY RANGE COLUMNS(create_time) (
    PARTITION p0 VALUES LESS THAN ('2010-01-01 00:00:00'),
    PARTITION p1 VALUES LESS THAN ('2011-01-01 00:00:00'),
    PARTITION p2 VALUES LESS THAN ('2012-01-01 00:00:00'),
    PARTITION p3 VALUES LESS THAN ('2013-01-01 00:00:00'),
    PARTITION p4 VALUES LESS THAN ('2014-01-01 00:00:00'),
    PARTITION p5 VALUES LESS THAN ('2015-01-01 00:00:00'),
    PARTITION p6 VALUES LESS THAN ('2016-01-01 00:00:00'),
    PARTITION p7 VALUES LESS THAN ('2017-01-01 00:00:00'),
    PARTITION p8 VALUES LESS THAN ('2018-01-01 00:00:00'),
    PARTITION p9 VALUES LESS THAN ('2019-01-01 00:00:00'),
    PARTITION p10 VALUES LESS THAN ('2020-01-01 00:00:00'),
    PARTITION p11 VALUES LESS THAN ('2021-01-01 00:00:00'),
    PARTITION p12 VALUES LESS THAN ('2022-01-01 00:00:00'),
    PARTITION p13 VALUES LESS THAN ('2023-01-01 00:00:00'),
    PARTITION p14 VALUES LESS THAN ('2024-01-01 00:00:00'),
    PARTITION p15 VALUES LESS THAN ('2025-01-01 00:00:00'),
    PARTITION p16 VALUES LESS THAN ('2026-01-01 00:00:00'),
    PARTITION p17 VALUES LESS THAN ('2027-01-01 00:00:00'),
    PARTITION p18 VALUES LESS THAN ('2028-01-01 00:00:00'),
    PARTITION p19 VALUES LESS THAN ('2029-01-01 00:00:00'),
    PARTITION p20 VALUES LESS THAN ('2030-01-01 00:00:00'),
    PARTITION p21 VALUES LESS THAN MAXVALUE
);

-- 目录状态表
--
-- 这个表一行的大小：4+32+8+2=46
--
-- 46*1000万=46*10MB=460MB
-- 46*5000万=46*50MB=2300MB=2.3GB
-- 46*1亿=46*100MB=4600MB=4.6GB
-- 46*5亿=46*500MB=23000MB=23GB

CREATE TABLE `dirstate1` (
    agentid INT NOT NULL,       -- 客户端标识，合法值是客户端信息表的主键范围
    dirid CHAR(32) NOT NULL,    -- 目录标识，和文件信息表中的目录标识是重复冗余字段
    create_time DATETIME NOT NULL, -- 目录创建时间
    dirstate SMALLINT DEFAULT 0,   -- 目录状态：未处理（0），迁出（1/2），迁回（3/4）……
    PRIMARY KEY (`create_time`, `agentid`, `dirstate`, `dirid`)
) ENGINE=InnoDB
  DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_bin;

-- 一级编目表

CREATE TABLE `level1tbl1` (
    tagcol CHAR(4),            -- 文件信息表中编目字段名：tag1 .. tag8
    tagval VARCHAR(64),        -- 文件信息表中编目字段的含义
    PRIMARY KEY (`tagcol`, `tagval`)
) ENGINE=InnoDB
  DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_bin;

-- 二级编目表

CREATE TABLE `level2tbl1` (
    fileid CHAR(32),            -- 文件信息表中的 fileid
    tagkey VARCHAR(64),         -- 编目的属性
    tagval VARCHAR(64),         -- 编目的值
    PRIMARY KEY (`tagkey`, `fileid`)
) ENGINE=InnoDB
  DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_bin;

-- 客户端信息表

CREATE TABLE `agentinfo1` (
    agentid INT NOT NULL,
    permission INT DEFAULT 0,
    comment VARCHAR(128),
    PRIMARY KEY (`agentid`)
) ENGINE=InnoDB
  DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_bin;

-- 文件操作日志表

CREATE TABLE `fileops1` (
    old_fileid CHAR(32) NOT NULL,
    new_fileid CHAR(32) NOT NULL,
    operation TINYINT NOT NULL,
    time DATETIME NOT NULL,
    comment VARCHAR(128),
    PRIMARY KEY (`time`, `old_fileid`, `new_fileid`, `operation`)
) ENGINE=InnoDB
  DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_bin;

-- 进度统计表

CREATE TABLE `progress1` (
    time DATETIME NOT NULL,
    nr_files_total BIGINT,
    nr_files_finished BIGINT,
    nr_files_left BIGINT,
    PRIMARY KEY (`time`)
) ENGINE=InnoDB
  DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_bin;

-- end
