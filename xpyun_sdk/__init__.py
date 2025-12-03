"""
芯烨云打印机SDK
提供远程小票/标签订单打印、状态查询、语音播报等服务
"""

try:
    from ._version import __version__
except ImportError:
    # 如果 _version.py 不存在，使用默认版本
    __version__ = "0.1.0"

__author__ = "SDK开发者"

from .client import XpyunClient
from .exceptions import XpyunError, XpyunAuthError, XpyunAPIError
from .printer_manager import PrinterManager
from .print_service import PrintService
from .query_service import QueryService
from .voice_service import VoiceService

__all__ = [
    "XpyunClient",
    "XpyunError",
    "XpyunAuthError",
    "XpyunAPIError",
    "PrinterManager",
    "PrintService",
    "QueryService",
    "VoiceService"
]