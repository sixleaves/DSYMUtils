#!/usr/bin/python
#coding:utf-8
import ssl
from com.sweetcs.dsym.dao.BuilderVersionDAO import BuilderVersionDAO

class DownloadDSYMService:

    def __init__(self):
        self.dao = BuilderVersionDAO()

    def download(self, url:str, toPath:str):
        # print(url, "===>", toPath)
        from urllib import request
        request.urlretrieve(
            url=url,
            filename=toPath)
        return toPath

