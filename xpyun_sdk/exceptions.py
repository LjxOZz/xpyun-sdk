"""
芯烨云打印机SDK异常类
"""


class XpyunError(Exception):
    """SDK基础异常类"""
    pass


class XpyunAuthError(XpyunError):
    """认证异常"""
    pass


class XpyunAPIError(XpyunError):
    """API调用异常"""
    def __init__(self, code, message, data=None):
        self.code = code
        self.message = message
        self.data = data
        super().__init__(f"API错误 {code}: {message}")


class XpyunNetworkError(XpyunError):
    """网络请求异常"""
    pass