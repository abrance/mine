# -*- coding: utf-8 -*-

import time
import datetime
import models
import requests
import json
from log import logger


class Config:
    pacs_url = ''
    online_date = ''
    request_time = ''


class RestOperation(object):
    def __init__(self):
        self.db = models.Database()
        self.pacs_url = Config.pacs_url

    def write_into_database(self, study_list, study_time):
        return self.db.query_client_study_push(study_list, study_time)

    def rest_study_lanwon(self, send_data):
        response = requests.post(self.pacs_url, headers={'content-type': 'application/json'},
                                 data=json.dumps(send_data), timeout=5)
        if response.status_code != requests.codes.ok:
            raise Exception("receive rest info error.")
        else:
            receive_info = json.loads(response.text)

        logger.info("receive from lanwon: {}".format(receive_info))

        if int(receive_info['code']) != 200:
            raise Exception("study_info error, start to retry.")

        study_list = receive_info['data']['studyUids']
        study_counts = receive_info['data']['count']

        if len(study_list) != study_counts:
            raise Exception("study count error.")

        return study_list

    @staticmethod
    def all_dates_obtain(deadline):
        all_dates = []
        start_date = Config.online_date
        while start_date < deadline:
            all_dates.append(start_date)
            dt = datetime.datetime.strptime(start_date, "%Y-%m-%d") + datetime.timedelta(1)
            start_date = dt.strftime("%Y-%m-%d")
        return all_dates

    def run(self):
        logger.info("start the process to obtain study ids.")
        try:
            while True:
                # 一天拉取一次
                # time.sleep(2)
                # current_time = datetime.datetime.now()
                # time_point = datetime.datetime.strptime(Config.request_time, '%H:%M:%S')
                # now_time = datetime.datetime.strptime(current_time.strftime('%H:%M:%S'), '%H:%M:%S')
                # delta_time = (now_time - time_point).total_seconds()
                # if delta_time > 5 or delta_time < 0:
                #     continue
                # # 开始studyId更新请求
                # all_dates = self.all_dates_obtain(current_time.strftime('%Y-%m-%d'))
                # failed_date = self.db.query_study_failed_date()
                # missed_date = self.db.query_study_missed_date(all_dates)
                # logger.info("failed date in database: {}".format(failed_date))
                # logger.info("missed date: {}".format(missed_date))
                # date_list = list(set(failed_date + missed_date))
                # date_list.sort()
                #
                # for date_i in date_list:
                #     result = False
                #     for i in range(3):
                #         try:
                #             data = {
                #                 'busiType': 'STUDY',
                #                 'code': 'querStudyUids',
                #                 'inputParam': date_i,
                #                 'userId': 'anyun',
                #                 'userName': '安云'
                #             }
                #             logger.info("request params: {}".format(data))
                #             study_list = self.rest_study_lanwon(data)
                #             result = self.write_into_database(study_list, current_time.strftime("%Y-%m-%d %H:%M:%S"))
                #             if result:
                #                 logger.info("push study id into database success.")
                #                 break
                #             else:
                #                 logger.info("push study id into database failed.")
                #
                #         except Exception as e:
                #             logger.info("handle lanwon request error: {}".format(e))
                #
                #     self.db.query_study_result_update(date_i, result)
                # time.sleep(5)

                # 改为 20 min 拉取 一次
                now = datetime.datetime.now()
                tw_min_later = now + datetime.timedelta(minutes=20)

                # 开始studyId更新请求
                # all_dates = self.all_dates_obtain(now.strftime('%Y-%m-%d'))
                # failed_date = self.db.query_study_failed_date()
                # missed_date = self.db.query_study_missed_date(all_dates)
                # logger.info("failed date in database: {}".format(failed_date))
                # logger.info("missed date: {}".format(missed_date))
                # date_list = list(set(failed_date + missed_date))
                # date_list.sort()

                # 简易版本
                all_dates = self.all_dates_obtain(now.strftime('%Y-%m-%d'))
                # failed_date = self.db.query_study_failed_date()
                missed_date = self.db.query_study_missed_date(all_dates)
                # logger.info("failed date in database: {}".format(failed_date))
                logger.info("missed date: {}".format(missed_date))
                date_list = list(set(missed_date))
                date_list.sort()

                # TODO 需不需要兼容之前的接口，既然是实时监控的，就没必要兼容之前的拉取前些天没有上传的study_id接口？

                for date_i in date_list:
                    result = False
                    for i in range(3):
                        try:
                            data = {
                                'busiType': 'STUDY',
                                'code': 'querStudyUids',
                                'inputParam': date_i,
                                'userId': 'anyun',
                                'userName': '安云'
                            }
                            logger.info("request params: {}".format(data))
                            study_list = self.rest_study_lanwon(data)
                            result = self.write_into_database(study_list,
                                                              now.strftime("%Y-%m-%d %H:%M:%S"))
                            if result:
                                logger.info("push study id into database success.")
                                break
                            else:
                                logger.info("push study id into database failed.")

                        except Exception as e:
                            logger.info("handle lanwon request error: {}".format(e))

                    self.db.query_study_result_update(date_i, result)

                time.sleep((tw_min_later-datetime.datetime.now()).total_seconds())

        except KeyboardInterrupt:
            logger.info("receive KeyboardInterrupt, process exit")
            import sys
            sys.exit(0)

        except Exception as e:
            logger.info("obtain study ids error: {}".format(e))
