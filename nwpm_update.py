import argparse
import json
import os
parser = argparse.ArgumentParser(description='Navigator MX Workpack Manager')
parser.add_argument('-uri', '--host', default='https://nwpm.nvcloud.org/', help='Download mirror from nwpm')


def update_nwpm(host):
    import time
    nwpm_url = host + 'nwpm/latest.zip?t=' + str(time.time())
    download_here(nwpm_url)
    print("nwpm is now up to date!")
    return 0


def download_here(url):
    import requests,os
    from contextlib import closing

    with closing(requests.get(url, stream=True)) as response:
        chunk_size = 1024
        content_size = int(response.headers['content-length'])
        """
        需要根据 response.status_code 的不同添加不同的异常处理
        """
        # print('content_size', content_size, response.status_code, )
        progress = ProgressBar('UPDATE'
                               , total=content_size
                               , unit="KB"
                               , chunk_size=chunk_size
                               , run_status="Downloading..."
                               , fin_status="Download Complete")
        # chunk_size = chunk_size < content_size and chunk_size or content_size
        with open('nwpm_update.zip', 'wb') as f:
            for data in response.iter_content(chunk_size=chunk_size):
                f.write(data)
                progress.refresh(count=len(data))
        unzip('nwpm_update.zip', './')
        os.remove('nwpm_update.zip')
        outputColor('na', 'Successfully updated Navigator MX!')


class ProgressBar(object):
    def __init__(self, title, count=0.0, run_status=None, fin_status=None, total=100.0, unit='', sep='/',
                 chunk_size=1.0):
        super(ProgressBar, self).__init__()
        self.info = "[%s] %s %.2f %s %s %.2f %s"
        self.title = title
        self.total = total
        self.count = count
        self.chunk_size = chunk_size
        self.status = run_status or ""
        self.fin_status = fin_status or " " * len(self.status)
        self.unit = unit
        self.seq = sep

    def __get_info(self):
        # 【名称】状态 进度 单位 分割线 总数 单位
        _info = self.info % (
        self.title, self.status, self.count / self.chunk_size, self.unit, self.seq, self.total / self.chunk_size,
        self.unit)
        return _info

    def refresh(self, count=1, status=None):
        self.count += count
        # if status is not None:
        self.status = status or self.status
        end_str = "\r"
        if self.count >= self.total:
            end_str = '\n'
            self.status = status or self.fin_status

        """
        没搞懂 print(end="")的用法
        ,在eric中打印的东西看不到
        ,在window控制台下单条语句刷新并不添加新的行
        """
        # print(,end="")的用法,可能会出现打印看不到的情况
        print(self.__get_info(), end=end_str, )


def getContent(url):
    import requests
    response = requests.get(url)
    data = response.content.decode('utf-8')
    return data


def unzip(zfile_path, unzip_dir):
    import os
    import zipfile
    try:
        with zipfile.ZipFile(zfile_path) as zfile:
            zfile.extractall(path=unzip_dir)
    except zipfile.BadZipFile as e:
        print(zfile_path + " is a bad zip file ,please check!")


def outputColor(color, str):
    if color == "na":
        print(str)
    else:
        colors = {
            'white': '30',
            'red': '31',
            'deep_yellow': '32',
            'light_yellow': '33',
            'blue': '34',
            'light_purple': '35',
            'ao': '36',
            'grey': '37',
            'light_grey': '38',
        }
        print("\033[1;" + colors[color] + "m " + str + " \033[0m")
    return 0


if __name__ == '__main__':
    import sys
    args = parser.parse_args()
    if args.host is not None:
        update_nwpm(args.host)
        sys.exit(0)