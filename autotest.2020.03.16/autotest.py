# -*- coding: utf-8 -*-

# 自动化功能性测试
#
# 基本的思路是每个测试用例一个函数，测试循环中不断地运行测试用例。一个
# 测试用例包含测试的上下文。
#
# 每个测试用例运行时，打印日志，表明运行的是哪个测试用例。
#
# mike
# 2020-03-10

import os
import sys
import imp
import shutil
import random

import utils
import studyops
import protocol

def test1_stage0(filename, filesize=-1):
    """随机生成测试文件"""
    if filesize < 0:
        filesize = random.randint(1, 300*1024) # [1, 300KiB]
    else:
        pass
    blocksize = 4096
    blockdata = "1234567890abcdef"[random.randint(0, 15)] * blocksize
    leftsize = filesize
    with open(filename, "wb") as f:
        while leftsize > 0:
            writesize = leftsize if leftsize < blocksize else blocksize
            block = blockdata[0:writesize]
            f.write(block.encode("utf-8"))
            leftsize = leftsize - writesize

def test1_stage1(sgw_addr, sgw_port, filename):
    """上传文件"""
    p = protocol.Protocol(sgw_addr, sgw_port)
    p.launch()
    rc = p.putfile1(filename)
    p.finish()
    return rc

def test1_stage2(sgw_addr, sgw_port, old_name, new_name):
    """下载文件"""
    shutil.move(old_name, new_name)
    p = protocol.Protocol(sgw_addr, sgw_port)
    p.launch()
    rc = p.getfile2(old_name)
    p.finish()
    if rc:
        # print("file {} successfully download!".format(old_name))
        pass
    else:
        # print("file {} download failed!".format(new_name))
        pass
    return rc

def test1_stage3(old_name, new_name):
    """比较文件。文件相同返回真，否则返回假。"""
    old_name_md5 = utils.calcmd5(old_name)
    new_name_md5 = utils.calcmd5(new_name)
    return old_name_md5 == new_name_md5

def test1(testconf):
    """测试上传下载文件

    0. 生成测试文件
    1. 上传文件
    2. 下载文件
    3. 比较文件

    """
    sgw_addr = testconf.sgw_addr
    sgw_port = testconf.sgw_port
    old_name = "test1.1"
    new_name = "test1.2"

    utils.removefile(old_name)
    utils.removefile(new_name)
    test1_stage0(old_name)
    test1_stage1(sgw_addr, sgw_port, old_name)
    test1_stage2(sgw_addr, sgw_port, old_name, new_name)
    return test1_stage3(old_name, new_name)

def test2(testconf):
    """测试上传下载文件

    异常情况：下载文件后，往文件后追加内容，这时两个文件的 md5 肯定会
    不一样。

    """
    sgw_addr = testconf.sgw_addr
    sgw_port = testconf.sgw_port
    old_name = "test2.1"
    new_name = "test2.2"

    utils.removefile(old_name)
    utils.removefile(new_name)
    test1_stage0(old_name)
    test1_stage1(sgw_addr, sgw_port, old_name)
    test1_stage2(sgw_addr, sgw_port, old_name, new_name)

    rc = test1_stage3(old_name, new_name)
    if rc:
        utils.xor(new_name, 0)
        rc = test1_stage3(old_name, new_name)
        if rc:
            # new_name 的内容已更改，下载文件和源文件的 md5 不应该再相同
            return False
        else:
            utils.xor(new_name, 0)
            rc = test1_stage3(old_name, new_name)
            return rc
    else:
        return False

def test3_download_file(sgw_addr, sgw_port, filename):
    # 使用偏移下载接口
    p = protocol.Protocol(sgw_addr, sgw_port)
    p.launch()
    rc = p.getfile3(filename)
    p.finish()
    return rc

def test3(testconf):
    """测试按偏移下载文件

    0. 生成测试文件，大小不为零
    1. 上传文件
    2. 使用偏移下载文件的接口进行下载
    3. 比较生成的文件和下载回来的文件
    """
    sgw_addr = testconf.sgw_addr
    sgw_port = testconf.sgw_port
    old_name = "test3.1"
    new_name = "test3.2"

    utils.removefile(old_name)
    utils.removefile(new_name)
    test1_stage0(old_name)
    test1_stage1(sgw_addr, sgw_port, old_name)

    shutil.move(old_name, new_name)
    rc = test3_download_file(sgw_addr, sgw_port, old_name)
    if rc:
        return test1_stage3(old_name, new_name)
    else:
        return False

def test4(testconf):
    """上传大小为零的文件"""
    filename = "test4.1"
    utils.removefile(filename)
    test1_stage0(filename, filesize=0)
    return test1_stage1(testconf.sgw_addr, testconf.sgw_port, filename)

def test5(testconf):
    """下载大小为零的文件"""
    filename = "test5.1"
    utils.removefile(filename)
    test1_stage0(filename, filesize=0)
    test1_stage1(testconf.sgw_addr, testconf.sgw_port, filename)
    utils.removefile(filename)
    rc = test3_download_file(testconf.sgw_addr, testconf.sgw_port, filename)
    if rc:
        filesize = os.path.getsize(filename)
        return filesize == 0
    else:
        return False

def test6(testconf):
    """测试获取 studyid 文件列表的接口

    0. 生成一个文件列表
    1. 按照这个文件列表生成一个目录
    2. 上传生成的这个目录
    3. 获取这个目录对应的 studyid 列表
    4. 对比生成的文件列表和获取的文件列表
    """

    def test6_stage0():
        """生成一个文件列表"""
        # print("test6_stage0")
        max_nr_files = 42
        return {
            "test6.file.{}".format(i): random.randint(1, 300*1024) for i in range(1, max_nr_files+1)
        }

    def test6_stage1(dirname, studyid, filelist):
        """根据文件列表在当前目录下生成文件，dirname/levelpath/studyid/files"""
        # print("test6_stage1")
        utils.removedir(dirname)
        levelpath = studyops.calcpath(studyid)
        leafdir = os.sep.join((dirname, levelpath, studyid))
        os.makedirs(leafdir)
        abscurpath = os.path.abspath(os.curdir)
        os.chdir(leafdir)
        for filename, filesize in filelist.items():
            test1_stage0(filename, filesize)
        os.chdir(abscurpath)

    def test6_stage2(sgw_addr, sgw_port, dirname, studyid, filelist):
        """上传生成的目录，上传的文件路径前面要求没有路径分隔符"""
        # print("test6_stage2")
        abscurpath = os.path.abspath(os.curdir)
        levelpath = studyops.calcpath(studyid)
        p = protocol.Protocol(sgw_addr, sgw_port)
        p.launch()
        os.chdir(dirname)
        for filename in filelist.keys():
            filepath = os.sep.join((levelpath, studyid, filename))
            p.putfile1(filepath)
        p.finish()
        os.chdir(abscurpath)

    def test6_stage3(sgw_addr, sgw_port, studyid):
        """获取 studyid 文件列表"""
        # print("test6_stage3")
        p = protocol.Protocol(sgw_addr, sgw_port)
        p.launch()
        filestat = p.getfilelist1(studyid)
        p.finish()
        return filestat["filelist"]

    def test6_stage4(filelist1, filelist2):
        """根据文件名，大小逐个文件对比两个文件列表

        其中，一个文件列表是生成的，另外一个文件列表是从服务器获取的。
        文件列表的格式是一个字典：{"filename": filesize, ...}

        """
        # print("test6_stage4")
        len1 = len(filelist1)
        len2 = len(filelist2)
        if len1 > 0 and len1 == len2:
            for filepath in filelist1.keys():
                filesize1 = filelist1[filepath]
                filesize2 = filelist2[filepath]
                if filesize1 == filesize2:
                    pass
                else:
                    # print("different filesize: filepath={}".format(filepath))
                    return False
            return True
        else:
            # print("different filelist")
            return False

    # 开始执行 test6 的测试用例
    dirname = "test6"
    studyid = "1.2.826.0.1.3680043.2.461.9701983.620200312"
    levelpath = studyops.calcpath(studyid)
    filelist1 = test6_stage0()
    test6_stage1(dirname, studyid, filelist1)
    test6_stage2(
        testconf.sgw_addr, testconf.sgw_port,
        dirname, studyid, filelist1
    )
    filepath1 = {
        os.path.join(os.sep, levelpath, studyid, filename): filesize
        for filename, filesize in filelist1.items()
    }
    filepath2 = {
        filename.replace(os.sep, "/"): filesize
        for filename, filesize in filepath1.items()
    }
    # import pprint
    # pprint.pprint(filepath2)
    filepath3 = test6_stage3(testconf.sgw_addr, testconf.sgw_port, studyid)
    # pprint.pprint(filepath3)
    return test6_stage4(filepath2, filepath3)

def run_test_plan(testconf):
    res = ["fail", "done"]
    for name, plan in testconf.plans.items():
        done = 0
        fail = 0
        test = 0
        for testname in plan:
            try:
                testfunc = eval(testname)
            except NameError as e:
                print("autotest terminated: no {}".format(testname))
                print("{}: {} test, {} done, {} fail".format(
                    name, test, done, fail)
                )
                sys.exit(-1)
            else:
                rc = testfunc(testconf)
                if rc:
                    done = done + 1
                else:
                    fail = fail + 1
                test = test + 1
                print("run {}.{}: {}".format(name, testname, res[int(rc)]))
        print("{}: {} test, {} done, {} fail".format(
            name, test, done, fail)
        )

def run_test_random(testconf):
    res = ["fail", "done"]
    done = 0
    fail = 0
    test = testconf.run_nr_times
    while testconf.run_nr_times > 0:
        n = random.randint(1, testconf.max_nr_test)
        testname = "test{}".format(n)
        try:
            testfunc = eval(testname)
        except NameError as e:
            print("autotest terminated: no {}".format(testname))
            print("run_test_random: {} test, {} done, {} fail".format(
                done+fail, done, fail
            ))
            sys.exit(-1)
        else:
            rc = testfunc(testconf)
            if rc:
                done = done + 1
            else:
                fail = fail + 1
            testconf.run_nr_times = testconf.run_nr_times - 1
            print("run random.{}: {}".format(testname, res[int(rc)]))
    print("run_test_random: {} test, {} done, {} fail".format(
        test, done, fail
    ))

def run_test(config_path):
    """根据配置文件指定的选项，运行计划测试"""
    basename = os.path.basename(config_path)
    module = imp.load_source(basename, config_path)

    if module.how_to_test == "plan":
        run_test_plan(module)
    elif module.how_to_test == "random":
        run_test_random(module)
    else:
        print("{}: invalid how_to_test={}".format(
            config_path, module.how_to_test)
        )

if __name__ == '__main__':
    try:
        nr_args = len(sys.argv)
        if nr_args > 1:
            for config_path in sys.argv[1:]:
                run_test(config_path)
        else:
            print("usage: {} <configpath> ...".format(sys.argv[0]))
            sys.exit(-1)
    except KeyboardInterrupt:
        sys.exit(0)
