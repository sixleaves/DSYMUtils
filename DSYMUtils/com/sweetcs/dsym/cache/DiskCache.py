import psutil
from collections import OrderedDict

from com.sweetcs.dsym.utils.FileUtils import FileUtils

class DiskCache(OrderedDict):
    # 最大2W条缓存记录
    def __init__(self, capacity=20000):
        self.capacity = capacity
        self.cache = OrderedDict()


    def get(self, key):
        if self.cache.__contains__(key):
            value = self.cache.pop(key)
            self.cache[key] = value
        else:
            value = None
        return value


    def set(self, key, value):

        item="Nothing"
        try:
            while(True):
                if DiskCache.isDiskFull() == False:
                    break
                item = self.popitem(last=False)
                url = item[0],path = item[1]
                FileUtils.deleteFile(path)

        except KeyError as e:
            pass
        finally:
            print("delete " + str(item))

        if self.cache.__contains__(key):
            value = self.cache.pop(key)
            self.cache[key] = value
        else:
            if len(self.cache) == self.capacity:
                self.cache.popitem(last=False)
                self.cache[key] = value
            else:
                self.cache[key] = value

    def has_key(self, key):
        return self.cache.__contains__(key)


    @classmethod
    def remainDisk(cls, path='/'):
        sdiskusage = psutil.disk_usage(path)
        return 100 - sdiskusage.percent

    # threshold 设置硬盘剩余空间的比例
    @classmethod
    def isDiskFull(cls, path='/', threshold=50):
        remain = cls.remainDisk(path)
        if remain < threshold:
            return True
        return False

if __name__ == '__main__':
    c = DiskCache()
    for i in range(5, 10):
        c.set(i, 10 * i)

    print(c.cache, c.cache.keys())

    c.get(5)
    c.get(7)

    print(c.cache, c.cache.keys())

    c.set(10, 100)

    # item = c.cache.popitem(last=False)
    # print(item[0], item[1])
    # print(c.cache, c.cache.keys())
    #
    # c.set(9, 44)
    # print(c.cache, c.cache.keys())
    # remain = DiskCache.remainDisk()
    # print(DiskCache.isDiskFull())