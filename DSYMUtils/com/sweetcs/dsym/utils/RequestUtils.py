
import requests

urlsMapEnv = {
    "qc-report-api.dev.web.nd": "development",                              # 开发环境
    "qc-report-api.debug.web.nd": "test",                                   # 测试环境
    "qc-report-api.beta.101.com": "preproduction",                          # 预生产环境
    "qc-report-api.sdp.101.com": "product"                                  # 生产环境
}
class RequestUtils:

    @classmethod
    def postRequest(cls, url = None, data = None, json = None, headers = None):
        if json != None:
            return requests.post(url, json=json, headers=headers)
        if data != None:
            return requests.post(url, data, headers)

    @classmethod
    def getRequest(cls,url = None, params = None):
        return requests.get(url=url, params=params)

    @classmethod
    def putRequest(cls,url = None, json={}, headers= {}):
        return requests.put(url=url, json=json, headers = headers)

    # 根据url地址返回所对应的环境
    @classmethod
    def getEnvWithUrl(cls, url = None):
        keys = urlsMapEnv.keys()
        for key in keys:
            if url.find(key) != -1:
                return urlsMapEnv.get(key)
        return "UndefineEnv"

if __name__ == '__main__':
    env =  RequestUtils.getEnvWithUrl("qc-report-api.sdp.101.com")
    print(env)