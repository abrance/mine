# @Time    : 2020/8/21 16:29
# @Author  : DaguguJ
# @Email   : 1103098607@qq.com
# @File    : split_path.py

path = '1000/root/'


def split(agent_path: str):
    i = agent_path.index('/')
    agent_id = agent_path[:i]
    _path = agent_path[i:].rstrip('/')
    if agent_id.isdigit():
        return agent_id, _path
    else:
        return False


if __name__ == '__main__':
    print(split(path))
