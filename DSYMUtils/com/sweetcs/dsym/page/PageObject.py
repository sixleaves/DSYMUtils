from com.sweetcs.dsym.config import RequestURIConfig, Constant
from com.sweetcs.dsym.utils.RequestUtils import RequestUtils


class PageObject:

    def __init__(self):
        self.isLast = False
        self.url = ""
        self.current_page_number = 0
        self.current_page_size = 100
        self.params = {}
        self.params["current_page_number"] = self.current_page_number
        self.params["current_page_size"] = self.current_page_size
        self.params["qc_report_version"] = RequestURIConfig.config().get(Constant.QC_REPORT_VERSION)



    def nextPage(self, interface:str, data_type="", iosMobileName=""):

        # 可能变化的三个参数, 需要重新设置
        self.params["current_page_size"] = self.current_page_size
        self.params["current_page_number"] = self.current_page_number

        if interface == Constant.REQUEST_UNCLASSIFY_DATA_INTERFACE:
            self.params["data_type"] = data_type
        elif interface == Constant.REQUEST_COMPOENT_SEARCH:
            self.params["iosMobileName"] = iosMobileName

        # /{qc_report_version}/data/{data_type}/component/unidentified?platform=iOS&size={current_page_size}&page={current_page_number}
        self.url = RequestURIConfig.getUrl(interface=interface,
                                           params=self.params
                                           )

        print(self.url)
        self.current_page_number += 1
        r = RequestUtils.getRequest(url=self.url)
        result = r.json()
        # print(json.dumps(result, indent=4))
        self.isLast = result["last"]

        if True == self.isLast: self.current_page_number = 0
        return result["content"], self.isLast