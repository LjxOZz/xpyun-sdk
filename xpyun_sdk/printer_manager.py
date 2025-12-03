"""
打印机管理模块
提供打印机管理相关功能
"""

from typing import List, Dict, Any, Optional
from .client import XpyunClient
from .exceptions import XpyunError


class PrinterManager:
    """打印机管理器"""

    def __init__(self, client: XpyunClient):
        """
        初始化打印机管理器

        Args:
            client: xpyun客户端实例
        """
        self.client = client

    def add_printer(self, sn: str, name: str, card: str = None) -> Dict[str, Any]:
        """
        添加单个打印机

        Args:
            sn: 打印机编号
            name: 打印机名称
            card: 打印机识别码（如已生成二维码可不填，系统自动生成）

        Returns:
            API响应数据
        """
        printer = {
            "sn": sn,
            "name": name
        }
        if card:
            printer["card"] = card

        return self.client.add_printers([printer])

    def add_printers(self, printers: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        批量添加打印机

        Args:
            printers: 打印机列表，每个打印机包含sn、name、card（可选）字段

        Returns:
            API响应数据

        Example:
            printers = [
                {"sn": "123456789", "name": "前台打印机"},
                {"sn": "987654321", "name": "后厨打印机", "card": "识别码"}
            ]
        """
        if not printers:
            raise XpyunError("打印机列表不能为空")

        # 验证打印机数据格式
        for printer in printers:
            if not printer.get('sn') or not printer.get('name'):
                raise XpyunError("每个打印机必须包含sn和name字段")

        return self.client.add_printers(printers)

    def delete_printer(self, sn: str) -> Dict[str, Any]:
        """
        删除单个打印机

        Args:
            sn: 打印机编号

        Returns:
            API响应数据
        """
        return self.client.del_printers([sn])

    def delete_printers(self, sn_list: List[str]) -> Dict[str, Any]:
        """
        批量删除打印机

        Args:
            sn_list: 打印机编号列表

        Returns:
            API响应数据
        """
        if not sn_list:
            raise XpyunError("打印机编号列表不能为空")

        return self.client.del_printers(sn_list)

    def update_printer_name(self, sn: str, name: str) -> Dict[str, Any]:
        """
        更新打印机名称

        Args:
            sn: 打印机编号
            name: 新的打印机名称

        Returns:
            API响应数据
        """
        if not sn or not name:
            raise XpyunError("打印机编号和名称不能为空")

        return self.client.upd_printer(sn, name)

    def clear_print_queue(self, sn: str) -> Dict[str, Any]:
        """
        清空打印机队列

        Args:
            sn: 打印机编号

        Returns:
            API响应数据
        """
        if not sn:
            raise XpyunError("打印机编号不能为空")

        return self.client.del_printer_queue(sn)

    def get_printer_status(self, sn: str) -> Dict[str, Any]:
        """
        获取单个打印机状态

        Args:
            sn: 打印机编号

        Returns:
            API响应数据，包含状态信息
        """
        if not sn:
            raise XpyunError("打印机编号不能为空")

        return self.client.query_printer_status(sn)

    def get_printers_status(self, sn_list: List[str]) -> Dict[str, Any]:
        """
        批量获取打印机状态

        Args:
            sn_list: 打印机编号列表

        Returns:
            API响应数据，包含状态信息
        """
        if not sn_list:
            raise XpyunError("打印机编号列表不能为空")

        return self.client.query_printers_status(sn_list)

    def get_printer_info(self, sn: str) -> Dict[str, Any]:
        """
        获取打印机详细信息

        Args:
            sn: 打印机编号

        Returns:
            包含打印机状态、队列等信息的字典
        """
        try:
            status_result = self.get_printer_status(sn)
            return {
                "sn": sn,
                "status": status_result.get("data"),
                "is_online": self._is_printer_online(status_result),
                "queue_status": self._get_queue_status(status_result)
            }
        except XpyunError:
            return {
                "sn": sn,
                "status": "unknown",
                "is_online": False,
                "queue_status": "unknown"
            }

    def _is_printer_online(self, status_data: Dict[str, Any]) -> bool:
        """
        判断打印机是否在线

        Args:
            status_data: 状态数据

        Returns:
            True表示在线，False表示离线
        """
        data = status_data.get("data")
        if not data:
            return False

        # 需要根据实际API返回格式解析状态
        # 这里假设data字段中的某个属性表示在线状态
        return data.get("connected", False)

    def _get_queue_status(self, status_data: Dict[str, Any]) -> str:
        """
        获取队列状态

        Args:
            status_data: 状态数据

        Returns:
            队列状态描述
        """
        data = status_data.get("data")
        if not data:
            return "unknown"

        # 需要根据实际API返回格式解析队列状态
        return data.get("queue_status", "normal")