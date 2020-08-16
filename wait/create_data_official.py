# coding: utf-8

import os
import time
import datetime
import Queue
import pymysql
import random


conn = pymysql.connect(host='127.0.0.1', user='root', passwd='123456', db='metadata', charset='utf8mb4')
cursor = conn.cursor()


def insert_into_db():
	# agent_id = 10000
	# study_id = '1.2.826.9.1.3680043.2.461.11334684.1087825620'
	# sql_index = ''
	for x in range(10):
		study_id = ('1.2.{}.9.1.3680043.2.461.11334684.').format(x)		

    		try:
			# counting = int(study_id[-10:])    # 尾数
			list0 = [study_id+'{}'.format(i) for i in range(1000000)]
			# list0 = [(study_id+str(i)) for i in range(1000000)]
			# list1 = [10000 for _ in range(1000000)]
			list1 = [random.randint(-1,10001) for _ in range(1000000)]
			# list2 = [datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') for _ in range(1000000)]
			list2 = [(datetime.datetime.now()-datetime.timedelta(days=random.randint(0,3600))).strftime('%Y-%m-%d %H:%M:%S') for _ in range(1000000)]
			# study_id += str(i)
			param = list(zip(list0, list1, list2))
                        print('waiting')
			# param = [(study_id+str(i), 10000, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) for i in range(10)]
			sql_index = "INSERT into study_index11(study_id, agent_id, create_time) VALUES(%s, %s, %s);"
                        print(len(param))
		except Exception as e:
			print("insert failed: %s" % sql_index)
	       	 	print(e)
		finally:
	        	cursor.executemany(sql_index, param)
	        	conn.commit()
                        


if __name__ == "__main__":
        t1 = datetime.datetime.now()
	insert_into_db()
        t = datetime.datetime.now()-t1
        print(t)
