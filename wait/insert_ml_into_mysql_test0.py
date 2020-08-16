import pymysql
import threading
import time
from queue import Queue
from DBUtils.PooledDB import PooledDB
import random


ini = {
    'agent_id' : 10000,    # 固定值，agent_id
    'create_time' : '2020-3-16 9:00:00',    # 固定值，create_time
    'count' : 100000,    # executemany每次执行多少行插入
    'insert_no': 10000000,    # 总插入数量
    'study_id_ini': '1.2.9.1.368{0}.2.461.1133{0}.'.format(random.randint(0, 100000)),    # 初始studyid
    'thread_no': 10    # 线程数量
}


class ThreadInsert(object):
    "多线程并发MySQL插入数据"
    def __init__(self):
        start_time = time.time()
        self.pool = self.mysql_connection()
        self.data = self.getData()
        # self.mysql_delete()
        self.task()
        print("========= 数据插入,共耗时:{}'s =========".format(round(time.time() - start_time, 3)))

    def mysql_connection(self):
        maxconnections = 15  # 最大连接数
        pool = PooledDB(
            pymysql,
            maxconnections,
            host='localhost',
            user='root',
            port=3306,
            passwd='123456',
            db='metadata',
            use_unicode=True)
        return pool

    def getData(self):
        study_id = ini.get('study_id_ini')
        insert_no = ini.get('insert_no')
        study_id_list = [study_id+'{}'.format(i) for i in range(insert_no)]   # 千万数据级别study_id
        agent_id_list = [0]*insert_no
        create_time_list = ['2020-3-16 9:00:00']*insert_no
        param_list = list(zip(study_id_list, agent_id_list, create_time_list))

        cnt = ini.get('count')
        return [param_list[i:i+cnt] for i in range(0, insert_no, cnt)]   # 把列表切分成cnt长度的小列表的列表


    def mysql_delete(self):
        st = time.time()
        con = self.pool.connection()
        cur = con.cursor()
        sql = "TRUNCATE TABLE test"
        cur.execute(sql)
        con.commit()
        cur.close()
        con.close()
        print("清空原数据.==>> 耗时:{}'s".format(round(time.time() - st, 3)))

    def mysql_insert(self, *args):
        con = self.pool.connection()
        cur = con.cursor()
        sql = "INSERT INTO study_index11(study_id, agent_id, create_time) VALUES(%s, %s, %s)"
        try:
            cur.executemany(sql, *args)
            con.commit()
        except Exception as e:
            con.rollback()  # 事务回滚
            print('SQL执行有误,原因:', e)
        finally:
            cur.close()
            con.close()

    def task(self):
        thread_no = ini.get('thread_no')
        q = Queue(maxsize=thread_no)  # 设定最大队列数和线程数
        st = time.time()
        while self.data:
            content = self.data.pop()
            t = threading.Thread(target=self.mysql_insert, args=(content,))
            q.put(t)
            if (q.full() == True) or (len(self.data)) == 0:
                thread_list = []
                while q.empty() == False:
                    t = q.get()
                    thread_list.append(t)
                    t.start()
                for t in thread_list:
                    t.join()
        print("数据插入完成.==>> 耗时:{}'s".format(round(time.time() - st, 3)))


if __name__ == '__main__':
    ThreadInsert()
