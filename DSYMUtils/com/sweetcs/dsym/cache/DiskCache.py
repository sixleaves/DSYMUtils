import psutil
from collections import OrderedDict
from com.sweetcs.dsym.utils.FileUtils import FileUtils
import json
import os
from com.sweetcs.dsym.config import CacheConfig
import threading

_set_lock = threading.Lock()
_io_lock = threading.Lock()

class DiskCache(OrderedDict):

    _instance_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            with cls._instance_lock:
                if not hasattr(cls, '_instance'):
                    cls._instance = super().__new__(cls)
        return cls._instance

    # 最大2W条缓存记录
    def __init__(self, capacity=20000):
        self.capacity = capacity
        self.cache = OrderedDict()

        # 初始化缓存文件
        self.cacheFilePath= CacheConfig.config().get(CacheConfig.PATH)
        self.cacheRootPath = FileUtils.getParentPath(self.cacheFilePath)
        if os.path.exists(self.cacheFilePath) == False:
            if os.path.exists(self.cacheRootPath) == False:
                try:
                    os.mkdir(self.cacheRootPath, mode=777)
                except PermissionError as e:
                    print("权限不够, 请手动创建缓存目录:{0}. 缓存配置文件在config包下的CacheConfig".format(self.cacheFilePath))
                    exit(-1)
            f = open(self.cacheFilePath, mode="w+")
            f.close()
        else:
            self.syncFromDisk()

    def get(self, key):
        if self.cache.__contains__(key):
            value = self.cache.pop(key)
            self.cache[key] = value
        else:
            value = None
        return value


    def set(self, key, value):

        global _set_lock
        _set_lock.acquire()

        item="Nothing"
        try:
            while(True):
                if DiskCache.isDiskFull() == False:
                    break
                item = self.popitem(last=False)
                url = item[0],path = item[1]
                FileUtils.deleteFile(path)

            if self.cache.__contains__(key):
                pass
            else:
                if len(self.cache) == self.capacity:
                    self.cache.popitem(last=False)
                    self.cache[key] = os.path.abspath(value)
                else:
                    self.cache[key] = os.path.abspath(value)
        except KeyError as e:
            pass
        finally:
            _set_lock.release()
            self.syncToDisk()

    # 将缓存信息同步到磁盘
    def syncToDisk(self):
        global _io_lock
        _io_lock.acquire()
        try:
            jsObj = json.dumps(self.cache)
            fileObject = open(self.cacheFilePath, 'w')
            fileObject.write(jsObj)
        finally:
            fileObject.close()
            _io_lock.release()

    # 将缓存信息同步到磁盘
    def syncFromDisk(self):
        global _io_lock
        _io_lock.acquire()
        try:
            fileObject = open(self.cacheFilePath, 'r')
            r = fileObject.readlines()
            if len(r) == 0:
                pass
            else:
                tempDict = json.loads(r[0])
                self.cache = OrderedDict(tempDict)

            # print(r, type(r))
        finally:
            fileObject.close()
            _io_lock.release()


    def has_key(self, key):
        return self.cache.__contains__(key)


    @classmethod
    def remainDisk(cls, path='/'):
        sdiskusage = psutil.disk_usage(path)
        return 100 - sdiskusage.percent

    # threshold 设置硬盘剩余空间的比例
    @classmethod
    def isDiskFull(cls, path='/', threshold=25):
        remain = cls.remainDisk(path)
        if remain < threshold:
            return True
        return False

if __name__ == '__main__':
    c = DiskCache()
    c2 = DiskCache()
    print(id(c), id(c2))

    # 'http://debug.s3.nds.sdp/release_app_fac_dysm/common-control-demo1499741291523_1525328997987-dSYM.zipdsym'
    # './15290540898014dsym'
    c.set("http://debug.s3.nds.sdp/release_app_fac_dysm/common-control-demo1499741291523_1525328997987-dSYM.zipdsym", "./15290540898014dsym")
    c.set("http://debug.s3.nds.sdp/release_app_fac_dysm/common-control-demo1499741291523_1525328997987-dSYM.zipdsym1", "./15290540898014dsym")
    c.set("http://debug.s3.nds.sdp/release_app_fac_dysm/common-control-demo1499741291523_1525328997987-dSYM.zipdsym2", "./15290540898014dsym")
    c.set("http://debug.s3.nds.sdp/release_app_fac_dysm/common-control-demo1499741291523_1525328997987-dSYM.zipdsym3", "./15290540898014dsym")
    c.set("http://debug.s3.nds.sdp/release_app_fac_dysm/common-control-demo1499741291523_1525328997987-dSYM.zipdsym4", "./15290540898014dsym")
    c.set("http://debug.s3.nds.sdp/release_app_fac_dysm/common-control-demo1499741291523_1525328997987-dSYM.zipdsym5", "./15290540898014dsym")
    print(c.has_key("http://debug.s3.nds.sdp/release_app_fac_dysm/common-control-demo1499741291523_1525328997987-dSYM.zipdsym"))
    print(c.get("http://debug.s3.nds.sdp/release_app_fac_dysm/common-control-demo1499741291523_1525328997987-dSYM.zipdsym"))

