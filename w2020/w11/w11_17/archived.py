"""
src_dir: agent路径
sgw_dir: sgw下的src_dir, sgw_save_path + agent_id + src_dir == sgw_dir

目标: archive(src_dir),  sgw_dir 将被归档，并进入刻录流程，并可以追踪到状态：未归档，
"""


class Agent(object):
    def __init__(self):
        self.filesystem = {}

    def get(self, path):
        self.filesystem.get(path)

