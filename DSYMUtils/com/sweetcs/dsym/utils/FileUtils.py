#coding:utf-8
import sys
class FileUtils:



    @staticmethod
    def getBasename(filePath):
        return str(filePath).split("/").pop()

    @staticmethod
    def getParentPath(filePath:str):
        end = filePath.strip("/").rindex("/")
        return filePath[:end]
