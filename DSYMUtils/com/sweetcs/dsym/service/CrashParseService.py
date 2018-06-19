
import re
import subprocess

from com.sweetcs.dsym.config import ParseRuleConfig
from com.sweetcs.dsym.domain.CrashStack import CrashStack
from com.sweetcs.dsym.domain.IndexObject import IndexObject
from com.sweetcs.dsym.utils.FileUtils import FileUtils




class CrashParseService:


    def __init__(self):

        self.crashStartLineFlag, self.crashEndLineFlag,self.isThreadType = ParseRuleConfig.config()

        # 固定参数
        self.cpuType = "ARM64"
        self.parseDWARCMDTemplate = "dwarfdump --lookup {symbolAddress} --arch {cpuType} {dsymPath}"
        self.paresATOSCMDTempate = "atos -arch arm64 -o {dsymPath} -l {loadAddress} {stackAddress}"
        self.dsymBinaryRelativePath = "/Contents/Resources/DWARF"

        # 用户提供的参数
        self.dsymPath = ""
        self.crashFilePath = ""

        # 需要计算的参数
        self.uuid = ""

        self.dsymFilename= ""
        self.appFilename = ""
        self.dsymBinaryAbsolutePath = ""

        self.slide = 0x00
        self.loadAddress = 0xFF
        self.cacheCrashFileBylines=[]

        self.lastExpIndexObj = IndexObject()
        self.threadExpIndexObj = IndexObject()

        self.threadNum = "-1"

        self.crashStack = CrashStack()


    # 初始化配置信息, 并提取崩溃文件对应的信息然后缓存
    def initConfig(self, dsymPath, crashFilePath, crashStack:list = None):


        self.dsymPath = dsymPath
        self.crashFilePath = crashFilePath

        self.dsymFilename = FileUtils.getBasename(dsymPath)
        self.appFilename = self.dsymFilename.split(".").pop(0)
        self.dsymBinaryAbsolutePath = self.dsymPath + self.dsymBinaryRelativePath + "/" + self.appFilename
        # print("dsymBinaryAbsolutePath:" + self.dsymBinaryAbsolutePath)
        # print("line" + str(sys._getframe().f_lineno) + ":"+ self.dsymBinaryAbsolutePath)
        self.cacheCrashFileBylines.clear()

        # 判断提供的是崩溃文件路径还是崩溃信息
        if crashFilePath != None and "" != crashFilePath:
            with open(crashFilePath, 'r', encoding='utf-8') as f:
                self.calcMemberParams(f.readlines())
        else:
            self.calcMemberParams(crashStack, isOriginCrashLines=False)

    def calcMemberParams(self, lines:list, isOriginCrashLines=True):

        # 如果不是原始崩溃文件, 而是处理后的崩溃行.那不用进行处理
        if isOriginCrashLines == False:
            self.threadExpIndexObj.beginIndex = 0
            self.threadExpIndexObj.endIndex = len(lines)
            self.cacheCrashFileBylines = lines
            return

        index = 0
        line, lineNum,index = self.readLine(lines, index=index)

        while line != None:
            try:
                if line.find("Slide") != -1:
                    self.slide = CrashParseService.str2num(line)  # 解析Slide值
                if line.find("Incident Identifier") != -1:
                    self.uuid = line.split(":")[1].strip()  # 解析获取app的uuid
                if line.find(self.appFilename) != -1:
                    try:
                        self.loadAddress = int(line.split(" ").pop(0), 16)  # 获取loadAddress
                        # print("line" + str(sys._getframe().f_lineno) + " loadAddress:"+str(self.loadAddress))
                    except ValueError as e:
                        self.loadAddress = 0XFF
                if line.find("Last Exception Backtrace:") != -1:  # 记录lastExceptionBackTrace的起始和结束位置
                    self.lastExpIndexObj.beginIndex = lineNum + 1
                    self.lastExpIndexObj.endIndex = lineNum + 2
                    # print(line)
                if line.find("Triggered by Thread:") != -1:  # 解析引起崩溃的线程号
                    self.threadNum = line.split(":").pop().strip()
                if line.find(self.crashStartLineFlag.format(threadNum=self.threadNum)) != -1:  # 记录崩溃线程号的其实位置和结束位置
                    self.threadExpIndexObj.beginIndex = lineNum + 1
                    while line != None or line != "":
                        line, lineNum, index = self.readLine(lines, index=index)

                        # 以这个来判断不太合适, 需要更改, 这些判断条件都要做成配置文件
                        # 方便后续维护
                        if len(line) == len(self.crashEndLineFlag) and line.find(self.crashEndLineFlag) != -1:
                            self.threadExpIndexObj.endIndex = lineNum + 1
                            break

                line, lineNum ,index= self.readLine(lines, index=index)
            except IndexError as e:
                line = None


    def readLine(self, f, index = 0):
        if isinstance(f, list):
            line = f[index]
            self.cacheCrashFileBylines.append(line)
            return line, index,index+1
        else:
            line = f.readline()
            self.cacheCrashFileBylines.append(line)
            return line, len(self.cacheCrashFileBylines) -1, 0


    def parseLineWithDWAR(self, stackAddress):
        symbolAddress = hex(stackAddress - self.slide)
        parseCMD = self.parseDWARCMDTemplate.format(symbolAddress = symbolAddress, cpuType = self.cpuType, dsymPath = self.dsymPath)

        print(parseCMD)

        res = subprocess.Popen(parseCMD, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
        result = res.stdout.readlines()
        for r in result:
            print(str(r, encoding="utf-8"))

    def parseLineWithATOS(self, stackAddress, originLine, isOutputOriginLine=False, lineNum="", offset=0x00):
        if isinstance(stackAddress, str):
            stackAddress = int(stackAddress, 16)
        if isinstance(offset, str):
            offset = int(offset, 10)
            # print(stackAddress)
        loadAddress = hex(int(stackAddress-offset))

        parseCMD = self.paresATOSCMDTempate.format(dsymPath=self.dsymBinaryAbsolutePath, loadAddress=str(loadAddress), stackAddress=str(hex(stackAddress)))
        # print(parseCMD, "loadAddress:" , loadAddress)
        res = subprocess.Popen(parseCMD, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
        result = res.stdout.readlines()
        # print(result)
        for r in result:
            parseResultLine = str(r, encoding="utf-8").strip()
            # print(line)
            if parseResultLine.startswith("0x"):   # 如果该行只有数字, 说
                # 明解析不出来, 原样输出改行即可
                if (False == isOutputOriginLine):  # 解析不出来, 控制是原样输出还是定制输出
                    tempLine = str(hex(stackAddress)) + ": 系统组件"
                    # print(tempLine)
                    self.crashStack.append(tempLine, isBusinessCompoentLine= False)
                else:
                    # print(originLine)
                    self.crashStack.append(originLine, isBusinessCompoentLine= False)
            else:                                  # 能够正常解析出来
                tempLine = lineNum + " " +  parseResultLine + "\n"
                # print(tempLine)
                self.crashStack.append(tempLine, isBusinessCompoentLine= True)
                # print(parseCMD)

    # 解析上一次崩溃堆栈
    def parseLastException(self):

        # print("line" + str(sys._getframe().f_lineno) + " :"+ str(sys._getframe().f_code.co_name))
        # print("====================LastException====================START=====================LastException\n")

        for line in self.cacheCrashFileBylines[self.lastExpIndexObj.beginIndex: self.lastExpIndexObj.endIndex]:
            lastExpStackAddrss = line.strip("() \n").split(" ")
            for stackAddress in lastExpStackAddrss:
                self.parseLineWithATOS(stackAddress, originLine=line)
        # print("====================LastException====================END=====================LastException\n")

    # 解析线程崩溃堆栈
    def parseThreadException(self):
        # print("line" + str(sys._getframe().f_lineno) + " :"+ str(sys._getframe().f_code.co_name))
        # print("====================ThreadException==================START===================ThreadException\n")
        for line in self.cacheCrashFileBylines[self.threadExpIndexObj.beginIndex: self.threadExpIndexObj.endIndex]:
            try:
                lineNum, stackAddress, offset = CrashParseService.getStackAddressAndOffset(line)
                self.parseLineWithATOS(stackAddress, originLine=line, isOutputOriginLine= True, lineNum=lineNum,offset=offset)
            except ValueError as e:
                # print(e)
                pass
        # print("====================ThreadException==================END===================ThreadException\n")


    def parse(self):
        # 每次解析之前重置crashStack对象
        self.crashStack.reset()
        self.parseThreadException()
        # for line in self.cacheCrashFileBylines:
        #     if line.find("Last Exception Backtrace:") != -1:
        #         # print(line)
        #         self.parseLastException()
        #     if line.find("Thread {0} Crashed:".format(self.threadNum)) != -1:
        #         self.parseThreadException()
        #         break

        # 返回崩溃解析后的崩溃堆栈
        return self.crashStack


    @staticmethod
    def str2num(lineStr):
        num = int("".join(list(filter(str.isdigit, lineStr))))
        return int(num)

    @staticmethod
    def getStackAddressAndOffset(line:str):
        try:
            p = re.compile(r"(\d+)\s+\S+\s*\w*(0x[a-f0-9]+)\s+.+\s+\+\s+(\d+)")
            match = p.match(line)
            return match.group(1),match.group(2),match.group(3)
        except Exception as e:
            print(e)



def test_parse_lastExceptionBacktrace():
    crashParseService = CrashParseService()
    crashParseService.initConfig(
        "/Users/sixleaves/Desktop/归档/common-control-demo1499741291523.app.dSYM",
        "/Users/sixleaves/Desktop/归档/common-control-demo1499741291523  2018-5-24 下午4-26.crash")
    backtraces = (
    0x183d12d8c,
    0x182ecc5ec,
    0x183cab750,
    0x183be40cc,
    0x183d12188,
    0x183bff0b4,
    0x102824f28,
    0x18d8eeee0,
    0x18d8eeacc,
    0x18dc2c3b4,
    0x18d99bac8,
    0x18d99b720,
    0x18d98f424,
    0x18d8e7770,
    0x187e8925c,
    0x187e8d3ec,
    0x187df9aa0,
    0x187e215d0,
    0x18dba55cc,
    0x183cba910,
    0x183cb8238,
    0x183cb8884,
    0x183bd8da8,
    0x185bbb020,
    0x18dbb978c,
    0x1027d6264,
    0x183669fc0)
    for stackAdd in backtraces:
        crashParseService.parseLineWithATOS(stackAdd)

def test_parse_threadException():
    crashParseService = CrashParseService()
    crashParseService.initConfig(
        "/Users/sixleaves/Desktop/归档/common-control-demo1499741291523.app.dSYM",
        "/Users/sixleaves/Desktop/归档/common-control-demo1499741291523  2018-5-24 下午4-26.crash")
    # crashParseService.parseLineWithATOS()
    crashParseService.parse()

if __name__ == "__main__":

    # crashParseService.parseLineWithDWAR(0x0000000102cdbc04)
    # crashParseService.parseLineWithDWAR(0x0000000102a30b34)
    # crashParseService.parseLineWithDWAR(0x00000001027d6264)
    # test_parse_lastExceptionBacktrace()
    # test_parse_threadException()
    print(CrashParseService.getStackAddressAndOffset("0   libsystem_kernel.dylib          0x00000001837992ec AAAAAAAAAAA + 140012"))
    print(CrashParseService.getStackAddressAndOffset("3   ...n-control-demo1499741291523\\\t0x0000000102cdbc04 AAAAAAAAAAA + 5291012"))




