import argparse
import json
import os

parser = argparse.ArgumentParser(description='Navigator MX Workpack Manager')
parser.add_argument('-uri', '--host', default='https://nwpm.nvcloud.org/', help='Download mirror from nwpm')
parser.add_argument('-install', '--install', help='Workpack Install')
parser.add_argument('-remove', '--remove', help='Workpack Remove')
# parser.add_argument('-u', '--update', help='Workpack Update')
parser.add_argument('-save', '--saveto', default='./workspace_pack', help='Workpack Update')
parser.add_argument('-create', '--create', help='Create a navigator space for this directory')
parser.add_argument('-delete', '--delete', help='Delete this navigator space')
parser.add_argument('-work', '--work', help='Run Workspace')


def install(packname, host, save_path):
    import time
    bit = myOS()[0]
    os = myOS()[1]
    if os == 'WindowsPE':
        arch = 'windows'

    if bit == '64bit':
        lens = '64'
    if bit == '32bit':
        lens = '32'
    target_version = arch+lens
    outputColor('na', "Handling request...")
    version_url = host + packname + '/versions.txt?t='+str(time.time())
    version_json = getContent(version_url)
    if isJSON(version_json):
        if 'error' in version_json:
            outputColor('red', "Cannot find package! If you want to release your own package, check the guides at https://nwpm.nvcloud.org/release_guide/")
        else:
            outputColor('na', "Already find workpack!")
            versions = json.loads(version_json)
            versions_latest = sorted(versions, reverse=True)[0]
            outputColor('na', "Latest version is: " + versions_latest)

            if target_version in versions[versions_latest]:
                url = host + packname + '/' + versions[versions_latest][target_version] + '?t=' + str(time.time())
                outputColor('na', "Prepare to download from " + url)
                filename = packname+versions_latest+target_version
                download(url, 'zip', filename, save_path, packname)
            else:
                outputColor('red', "Cannot find a version fit your device!")

    return 0


def remove(packname, save_path):
    import shutil,os
    if os.path.isdir(save_path + '/' + packname) is False:
        outputColor('na', 'Workpack is not installed!')
    else:
        outputColor('na', 'Removing workpack...')
        shutil.rmtree(save_path + '/' + packname)
        outputColor('na', 'Workpack ' + packname + ' removed successfully!')
    return 0


def update():
    return 0


def init(host, version):
    import time
    # 获取依赖
    pip_url = host + '_init_/' + version + '/pip.json?t='+str(time.time())
    pip = getContent(pip_url)
    if isJSON(pip):
        pipjson = json.loads(pip)
        if 'error' in pipjson:
            outputColor('red', "Cannot find init json in " + pip_url + " !")
            exit(0)
        else:
            for cmd in pipjson:
                os.system(cmd)
    else:
        outputColor('red', "Cannot find init json!")
        exit(0)
    outputColor('na', "Lib installed!")

    init_url = host + '_init_/' + version + '/_init_.zip?t='+str(time.time())
    download_here(init_url)
    # Create Workspace

    return 0


def delete(host,version):
    import shutil, os, time
    pip_url = host + '_init_/' + version + '/unpip.json?t=' + str(time.time())
    pip = getContent(pip_url)
    if isJSON(pip):
        pipjson = json.loads(pip)
        if 'error' in pipjson:
            outputColor('red', "Cannot find uninstall json in " + pip_url + " !")
            exit(0)
        else:
            for cmd in pipjson:
                os.system(cmd)
    else:
        outputColor('red', "Cannot find uninstall json!")
        exit(0)
    outputColor('na', "Lib uninstalled!")


    if os.path.isdir('nvGluon'):
        shutil.rmtree('nvGluon')
    if os.path.isdir('nvlib'):
        shutil.rmtree('nvlib')
    if os.path.exists('core_func.py'):
        os.remove('core_func.py')
    if os.path.exists('navigatormx.conf'):
        os.remove('navigatormx.conf')
    if os.path.exists('work.py'):
        os.remove('work.py')
    return 0


def work(pack):
    if os.path.exists('navigatormx.conf'):
        if os.path.exists('work.py'):
            # print('Please make sure you have edited the nxvigatormx.conf and set the workspace_pack to ' + pack + ' !')
            # edit conf
            conf = json.load(open('navigatormx.conf'))
            conf['workspace_pack'] = pack
            json.dump(conf, open('navigatormx.conf', 'w'))
            if os.path.isdir('workspace_pack/' + pack + '/nvlib') is False:
                os.mkdir('workspace_pack/' + pack + '/nvlib')
                copy_dir('nvlib', 'workspace_pack/' + pack + '/nvlib')
            os.system('python work.py')
        else:
            print('You don\'t have a work.py file in your directory!')
    else:
        print('You don\'t have a navigatormx.conf file in your directory!')

    return 0


def copy_dir(dir,newdir):
    from shutil import copy
    import os
    for p in os.listdir(dir):
        filepath=newdir+'/'+p
        oldpath=dir+'/'+p
        if os.path.isdir(oldpath):
            os.mkdir(filepath)
            copy_dir(oldpath,filepath)
        if os.path.isfile(oldpath):
            copy(oldpath,filepath)


def download(url, ext , filename, save_path, dir_name):
    import requests,os
    from contextlib import closing

    with closing(requests.get(url, stream=True)) as response:
        chunk_size = 1024
        content_size = int(response.headers['content-length'])
        """
        需要根据 response.status_code 的不同添加不同的异常处理
        """
        # print('content_size', content_size, response.status_code, )
        progress = ProgressBar(filename
                               , total=content_size
                               , unit="KB"
                               , chunk_size=chunk_size
                               , run_status="Downloading..."
                               , fin_status="Download Complete")
        # chunk_size = chunk_size < content_size and chunk_size or content_size
        if os.path.isdir(save_path) is False:
            os.mkdir(save_path)
        with open('{}{}{}.{}'.format(save_path, '\\', filename, ext), 'wb') as f:
            for data in response.iter_content(chunk_size=chunk_size):
                f.write(data)
                progress.refresh(count=len(data))
        unzip('{}{}{}.{}'.format(save_path, '\\', filename, ext),'./' + save_path + '/' + dir_name)
        os.remove('{}{}{}.{}'.format(save_path, '\\', filename, ext))
        outputColor('na', 'Successfully installed [' + dir_name + '] at your workpack root!')


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
        progress = ProgressBar('INIT'
                               , total=content_size
                               , unit="KB"
                               , chunk_size=chunk_size
                               , run_status="Downloading..."
                               , fin_status="Download Complete")
        # chunk_size = chunk_size < content_size and chunk_size or content_size
        with open('_init_.zip', 'wb') as f:
            for data in response.iter_content(chunk_size=chunk_size):
                f.write(data)
                progress.refresh(count=len(data))
        unzip('_init_.zip', './')
        os.remove('_init_.zip')
        outputColor('na', 'Successfully create Navigator MX!')


def getContent(url):
    import requests
    response = requests.get(url)
    data = response.content.decode('utf-8')
    return data


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


def isJSON(that_json):
    try:
        json_object = json.loads(that_json)
    except:
        return False
    return True


def myOS():
    import platform
    return platform.architecture()


def unzip(zfile_path, unzip_dir):
    import os
    import zipfile
    try:
        with zipfile.ZipFile(zfile_path) as zfile:
            zfile.extractall(path=unzip_dir)
    except zipfile.BadZipFile as e:
        print(zfile_path + " is a bad zip file ,please check!")


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


if __name__ == '__main__':
    import sys
    # pyinstall -F -c nwpm.py
    # print('Welcome to Navigator Workspace Pack Manager!')
    args = parser.parse_args()
    if args.install is not None:
        install(args.install, args.host, args.saveto)
        sys.exit()
    elif args.remove is not None:
        remove(args.remove, args.saveto)
        sys.exit()
    elif args.create is not None:
        init(args.host, args.create)
        sys.exit()
    elif args.delete is not None:
        delete(args.host, args.delete)
        sys.exit()
    elif args.work is not None:
        work(args.work)
        sys.exit()
