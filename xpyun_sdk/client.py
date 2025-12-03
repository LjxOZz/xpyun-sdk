"""
芯烨云打印机客户端
提供统一的API调用接口
"""

import json
import time
from typing import Dict, Any, Optional
import requests

from .auth import XpyunAuth
from .exceptions import XpyunError, XpyunAuthError, XpyunAPIError, XpyunNetworkError


class XpyunClient:
    """芯烨云打印机客户端"""

    BASE_URL = "https://open.xpyun.net/api/openapi/xprinter"
    TIMEOUT = 30

    def __init__(self, user: str, user_key: str, debug: bool = False):
        """
        初始化客户端

        Args:
            user: 用户ID
            user_key: 用户密钥
            debug: 是否开启调试模式
        """
        self.auth = XpyunAuth(user, user_key)
        self.debug = debug
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json;charset=UTF-8',
            'User-Agent': f'xpyun-sdk-python/0.1.0'
        })

    def _make_request(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        发送API请求

        Args:
            method: API方法名
            params: 请求参数

        Returns:
            API响应数据

        Raises:
            XpyunError: API调用失败
        """
        # 准备请求数据
        request_data = self.auth.get_auth_params()
        request_data['requestTime'] = int(time.time() * 1000)  # 毫秒时间戳

        if params:
            request_data.update(params)

        try:
            if self.debug:
                print(f"请求数据: {json.dumps(request_data, ensure_ascii=False, indent=2)}")

            # 发送POST请求
            response = self.session.post(
                f"{self.BASE_URL}/{method}",
                json=request_data,
                timeout=self.TIMEOUT
            )
            response.raise_for_status()

            # 解析响应
            result = response.json()

            if self.debug:
                print(f"响应数据: {json.dumps(result, ensure_ascii=False, indent=2)}")

            # 检查API返回状态
            if result.get('code') != 0:
                raise XpyunAPIError(
                    code=result.get('code'),
                    message=result.get('msg', '未知错误'),
                    data=result.get('data')
                )

            return result

        except requests.exceptions.RequestException as e:
            raise XpyunNetworkError(f"网络请求失败: {str(e)}")
        except json.JSONDecodeError as e:
            raise XpyunError(f"响应解析失败: {str(e)}")
        except XpyunAPIError:
            raise
        except Exception as e:
            raise XpyunError(f"未知错误: {str(e)}")

    def add_printers(self, printers: list) -> Dict[str, Any]:
        """
        添加打印机

        Args:
            printers: 打印机列表,每个打印机包含sn、name等字段

        Returns:
            API响应数据
        """
        return self._make_request("addPrinters", {"items": printers})

    def print_ticket(self,
                     sn: str,
                     content: str,
                     times: int = 1,
                     code_u: str = "",
                     mode: int = 0,
                     voice: int = 0) -> Dict[str, Any]:
        """
        打印小票

        Args:
            sn: 打印机编号
            content: 打印内容
            times: 打印份数
            code_u: 更新编号(可选)
            mode:  打印模式(0:自动, 1:强制打印)
            voice: 语音播报(0:关闭, 1:开启)

        Returns:
            API响应数据
        """
        params = {
            "sn": sn,
            "content": content,
            "times": times,
            "mode": mode,
            "voice": voice
        }
        if code_u:
            params["code_u"] = code_u

        return self._make_request("print", params)

    def print_label(self,
                    sn: str,
                    content: str,
                    height: int,
                    quantity: int = 1,
                    width: int = 30,
                    top: int = 0,
                    left: int = 0,
                    code_u: str = "") -> Dict[str, Any]:
        """
        打印标签

        Args:
            sn: 打印机编号
            content: 标签内容
            height: 标签高度
            quantity: 打印数量
            width: 标签宽度
            top: 上边距
            left: 左边距
            code_u: 更新编号（可选）

        Returns:
            API响应数据
        """
        params = {
            "sn": sn,
            "content": content,
            "height": height,
            "quantity": quantity,
            "width": width,
            "top": top,
            "left": left
        }
        if code_u:
            params["code_u"] = code_u

        return self._make_request("printLabel", params)

    def del_printers(self, sn_list: list) -> Dict[str, Any]:
        """
        删除打印机

        Args:
            sn_list: 要删除的打印机编号列表

        Returns:
            API响应数据
        """
        return self._make_request("delPrinters", {"snlist": sn_list})

    def upd_printer(self, sn: str, name: str) -> Dict[str, Any]:
        """
        更新打印机名称

        Args:
            sn: 打印机编号
            name: 新的打印机名称

        Returns:
            API响应数据
        """
        return self._make_request("updPrinter", {"sn": sn, "name": name})

    def del_printer_queue(self, sn: str) -> Dict[str, Any]:
        """
        清空打印机队列

        Args:
            sn: 打印机编号

        Returns:
            API响应数据
        """
        return self._make_request("delPrinterQueue", {"sn": sn})

    def query_order_state(self, order_id: str) -> Dict[str, Any]:
        """
        查询订单状态

        Args:
            order_id: 订单ID

        Returns:
            API响应数据
        """
        return self._make_request("queryOrderState", {"orderId": order_id})

    def query_order_statistics(self, sn: str, start_time: str, end_time: str) -> Dict[str, Any]:
        """
        查询订单统计

        Args:
            sn: 打印机编号
            start_time: 开始时间（YYYYMMDD）
            end_time: 结束时间（YYYYMMDD）

        Returns:
            API响应数据
        """
        return self._make_request("queryOrderStatis", {
            "sn": sn,
            "dateFrom": start_time,
            "dateTo": end_time
        })

    def query_printer_status(self, sn: str) -> Dict[str, Any]:
        """
        查询单个打印机状态

        Args:
            sn: 打印机编号

        Returns:
            API响应数据
        """
        return self._make_request("queryPrinterStatus", {"sn": sn})

    def query_printers_status(self, sn_list: list) -> Dict[str, Any]:
        """
        批量查询打印机状态

        Args:
            sn_list: 打印机编号列表

        Returns:
            API响应数据
        """
        return self._make_request("queryPrintersStatus", {"snlist": sn_list})

    def set_voice_type(self, sn: str, voice_type: int, voice: int = None) -> Dict[str, Any]:
        """
        设置语音类型

        Args:
            sn: 打印机编号
            voice_type: 语音类型
            voice: 语音播报开关（可选）

        Returns:
            API响应数据
        """
        params = {"sn": sn, "voiceType": voice_type}
        if voice is not None:
            params["voice"] = voice

        return self._make_request("setVoiceType", params)

    def play_voice(self, sn: str, voice_type: str, pay_type: int = None) -> Dict[str, Any]:
        """
        播放语音

        Args:
            sn: 打印机编号
            voice_type: 语音类型
            pay_type: 支付方式（可选）

        Returns:
            API响应数据
        """
        params = {"sn": sn, "voiceType": voice_type}
        if pay_type is not None:
            params["payType"] = pay_type

        return self._make_request("playVoice", params)