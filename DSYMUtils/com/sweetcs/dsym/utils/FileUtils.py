#coding:utf-8
import os
import shutil
class FileUtils:

    @staticmethod
    def copy(srcPath, toPath):
        pass

    # 获取文件名, 包含文件拓展名
    @staticmethod
    def getBasename(filePath):
        return str(filePath).split("/").pop()

    # 获取filePath的上级路径
    @staticmethod
    def getParentPath(filePath:str):
        end = filePath.strip("/").rindex("/")
        return filePath[:end]

    # 获取文件名, 不包含文件拓展名
    @staticmethod
    def getFileNameNoExtensions(filePath:str):
        tempName = FileUtils.getBasename(filePath)
        return tempName.split(".").pop(0).split("/").pop(-1)


    # 从dir目录中获取包含extension后缀的文件的绝对路径
    @staticmethod
    def getAbsolutelyPathFromDirWithExtension(dirPath:str, extension:str, isGetFirstOnly = False):
        dirPath = dirPath.strip("/")
        filenames=os.listdir(dirPath)
        filePaths = []
        for filename in filenames:
            if filename.endswith(extension):
                filePath = dirPath + "/" + filename
                if isGetFirstOnly == True:
                    return filePath
                filePaths.append(filePath)
        return filePaths

    @staticmethod
    def deleteFile(filePath:str):
        os.remove(filePath)

    @staticmethod
    def deleteDirs(dirPath:str):
        shutil.rmtree(dirPath)