import sys
import time
from datetime import datetime
from threading import Thread

import requests
import json


init_time = ''
stop_time = ''


class Controller(Thread):
    """
    控制运行
    """
    def __init__(self):
        super(Controller, self).__init__()
        self.loop()

    @staticmethod
    def rest_study_lanwon(test=False):
        """
        实际 请求
        :return: study list
        """
        if test:
            return ['test_{}'.format(i) for i in range(500)]
        url = ''
        data = {
            'busiType': 'STUDY',
            'code': 'querStudyUids',
            'inputParam': datetime.today().date,
            'userId': 'anyun',
            'userName': '安云'
        }

        response = requests.post(
            url,
            headers={'content-type': 'application/json'},
            data=json.dumps(data),
            timeout=5
        )

        assert response.ok
        receive_info = response.json()

        print("receive from lanwon: {}".format(receive_info))

        assert receive_info == "200"
        assert receive_info['data']['studyUids'] and receive_info['data']['count']

        study_list = receive_info['data']['studyUids']
        study_counts = receive_info['data']['count']
        assert study_counts == len(study_list)

        return study_list

    @staticmethod
    def write(stream, dest='file', filename='request_log'):
        """
        record
        :param stream:
        :param dest:
        :param filename:
        :return:
        """
        if dest == 'file':
            with open(filename, 'a') as file:
                file.write('\n{}\n{}\nEOF'.format(datetime.now(), stream))
        else:
            print('\n{}\n{}\nEOF'.format(datetime.now(), stream))
        return True

    def loop(self):
        """
        请求结果应该写入文件 作为分析使用
        :return:
        """
        while True:
            if init_time and stop_time:
                h, m = init_time.split(':')
                e_h, e_m = stop_time.split(':')
                _init_time = datetime.now().replace(hour=h, minute=m)
                _stop_time = datetime.now().replace(hour=e_h, minute=e_m)
                assert _stop_time > _init_time
                now = datetime.now()
                if _init_time < now < _stop_time:
                    pass
                elif _init_time > now:
                    time.sleep((_init_time-now).total_seconds())
                elif now > _stop_time:
                    print('today is pass')
                    sys.exit()
                else:
                    # unexpected
                    raise Exception
            else:
                pass

            self.run()
            time.sleep(20*60)

    def run(self) -> None:
        study_ls = self.rest_study_lanwon(test=True)
        self.write(study_ls)


if __name__ == '__main__':
    c = Controller()
