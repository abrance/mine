"""
客户端回迁
"""
import json

import requests


name = r'1.2.826.0.1.3680043.2.461.11803345.2998323732/1.2.826.0.1.3680043.2.461.11803345.2998323731.ini'
data = {
    'file_name': name,
    'back_place': 'F:\\data'
}

if __name__ == '__main__':

    from datetime import datetime
    t = datetime.now()
    response = requests.get(url='http://%s:%s/moveback.do' % ('127.0.0.1', '5000'),
                            headers={'content-type': 'application/json'},
                            data=json.dumps(data))
    t2 = (datetime.now() - t).total_seconds()
    print(t2)
    assert response.ok
    print(response.text)
