from pathlib import Path

FILE_PATH = './test'
file = Path(FILE_PATH).resolve()
NEW_FILE_PATH = FILE_PATH+'_new'
new_file = Path(NEW_FILE_PATH).resolve()


def rm_file_comment(f_path, new_f_path):
    with open(f_path, 'r') as _file:
        with open(new_f_path, 'w12_25') as _new_file:
            for line in _file.readlines():
                if '//' in line:
                    keep, _ = line.split('//', 1)
                    _new_file.write(keep+'\n')
                else:
                    _new_file.write(line)


if __name__ == '__main__':
    rm_file_comment(file, new_file)
