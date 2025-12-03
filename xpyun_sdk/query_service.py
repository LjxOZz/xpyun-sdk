"""
查询服务模块
提供订单、统计、状态查询功能
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from .client import XpyunClient
from .exceptions import XpyunError


class QueryService:
    """查询服务"""

    def __init__(self, client: XpyunClient):
        """
        初始化查询服务

        Args:
            client: xpyun客户端实例
        """
        self.client = client

    def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """
        获取订单状态

        Args:
            order_id: 订单ID

        Returns:
            订单状态信息
        """
        if not order_id:
            raise XpyunError("订单ID不能为空")

        result = self.client.query_order_state(order_id)
        return self._parse_order_status(result)

    def get_order_statistics(self,
                           sn: str,
                           start_date: str = None,
                           end_date: str = None,
                           days: int = 1) -> Dict[str, Any]:
        """
        获取订单统计数据

        Args:
            sn: 打印机编号
            start_date: 开始日期（YYYYMMDD格式），如果不提供则使用days参数
            end_date: 结束日期（YYYYMMDD格式），如果不提供则使用今天
            days: 统计天数（当start_date/end_date未提供时使用），默认1天

        Returns:
            订单统计数据
        """
        if not sn:
            raise XpyunError("打印机编号不能为空")

        if not start_date or not end_date:
            # 自动计算日期范围
            end = datetime.now()
            start = end - timedelta(days=days-1)

            start_date = start.strftime('%Y%m%d')
            end_date = end.strftime('%Y%m%d')

        result = self.client.query_order_statistics(sn, start_date, end_date)
        return self._parse_statistics(result)

    def get_printer_status(self, sn: str) -> Dict[str, Any]:
        """
        获取打印机状态

        Args:
            sn: 打印机编号

        Returns:
            打印机状态信息
        """
        if not sn:
            raise XpyunError("打印机编号不能为空")

        result = self.client.query_printer_status(sn)
        return self._parse_printer_status(result)

    def get_printers_status(self, sn_list: List[str]) -> Dict[str, Any]:
        """
        批量获取打印机状态

        Args:
            sn_list: 打印机编号列表

        Returns:
            批量状态信息
        """
        if not sn_list:
            raise XpyunError("打印机编号列表不能为空")

        result = self.client.query_printers_status(sn_list)
        return self._parse_printers_status(result)

    def is_printer_online(self, sn: str) -> bool:
        """
        检查打印机是否在线

        Args:
            sn: 打印机编号

        Returns:
            True表示在线，False表示离线
        """
        status = self.get_printer_status(sn)
        return status.get('is_online', False)

    def get_printer_info(self, sn: str) -> Dict[str, Any]:
        """
        获取打印机详细信息

        Args:
            sn: 打印机编号

        Returns:
            包含状态、统计等详细信息的字典
        """
        if not sn:
            raise XpyunError("打印机编号不能为空")

        # 获取状态信息
        status = self.get_printer_status(sn)

        # 获取今日统计数据
        today_stats = self.get_order_statistics(sn, days=1)

        # 获取昨日统计数据
        yesterday_stats = self.get_order_statistics(sn, days=1)

        return {
            "sn": sn,
            "status": status,
            "today_stats": today_stats,
            "yesterday_stats": yesterday_stats,
            "is_online": status.get('is_online', False),
            "last_update": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

    def get_system_status(self) -> Dict[str, Any]:
        """
        获取系统状态信息

        Returns:
            系统状态信息
        """
        # 获取所有打印机状态作为系统状态
        # 注意：这里需要您提供一个打印机编号列表，或者使用已添加的打印机
        return {
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "status": "normal"  # 需要根据实际情况判断
        }

    def search_orders(self,
                     order_id: str = None,
                     sn: str = None,
                     date_range: tuple = None,
                     status: str = None) -> List[Dict[str, Any]]:
        """
        搜索订单（注意：需要云平台支持订单历史查询）

        Args:
            order_id: 订单ID（模糊匹配）
            sn: 打印机编号
            date_range: 日期范围（start_date, end_date）
            status: 订单状态

        Returns:
            订单列表
        """
        # 注意：此功能需要云平台API支持订单搜索
        # 如果API不支持，可以返回空列表或抛出异常
        raise NotImplementedError("订单搜索功能需要云平台API支持")

    def _parse_order_status(self, api_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        解析订单状态响应

        Args:
            api_response: API原始响应

        Returns:
            解析后的订单状态
        """
        data = api_response.get("data", {})

        return {
            "order_id": data.get("orderId"),
            "status": data.get("state"),
            "print_status": data.get("printStatus"),
            "print_time": data.get("printTime"),
            "printer_sn": data.get("sn"),
            "is_completed": data.get("state") == "completed",
            "is_failed": data.get("state") == "failed",
            "raw_data": data
        }

    def _parse_statistics(self, api_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        解析统计数据响应

        Args:
            api_response: API原始响应

        Returns:
            解析后的统计数据
        """
        data = api_response.get("data", {})

        return {
            "print_orders": data.get("printCount", 0),
            "failed_orders": data.get("failedCount", 0),
            "success_rate": self._calculate_success_rate(
                data.get("printCount", 0),
                data.get("failedCount", 0)
            ),
            "date_range": {
                "start": data.get("dateFrom"),
                "end": data.get("dateTo")
            },
            "raw_data": data
        }

    def _parse_printer_status(self, api_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        解析打印机状态响应

        Args:
            api_response: API原始响应

        Returns:
            解析后的状态信息
        """
        data = api_response.get("data", {})

        return {
            "sn": data.get("sn"),
            "is_online": data.get("connected", False),
            "has_paper": data.get("hasPaper", False),
            "temperature": data.get("temperature"),
            "voltage": data.get("voltage"),
            "queue_length": data.get("queueLength", 0),
            "last_update": data.get("lastUpdateTime"),
            "raw_data": data
        }

    def _parse_printers_status(self, api_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        解析批量打印机状态响应

        Args:
            api_response: API原始响应

        Returns:
            解析后的状态信息
        """
        data = api_response.get("data", {})
        printers = []

        # 假设返回格式是字典，键是SN，值是状态信息
        for sn, status in data.items():
            printers.append({
                "sn": sn,
                "is_online": status.get("connected", False),
                "has_paper": status.get("hasPaper", False),
                "queue_length": status.get("queueLength", 0),
                "raw_data": status
            })

        return {
            "total": len(printers),
            "online_count": sum(1 for p in printers if p["is_online"]),
            "offline_count": sum(1 for p in printers if not p["is_online"]),
            "printers": printers
        }

    def _calculate_success_rate(self, total: int, failed: int) -> float:
        """
        计算成功率

        Args:
            total: 总订单数
            failed: 失败订单数

        Returns:
            成功率百分比
        """
        if total == 0:
            return 0.0
        success_rate = ((total - failed) / total) * 100
        return round(success_rate, 2)

    def generate_report(self,
                       sn: str,
                       report_type: str = "daily",
                       date: str = None) -> Dict[str, Any]:
        """
        生成报告

        Args:
            sn: 打印机编号
            report_type: 报告类型（daily: 日报，weekly: 周报，monthly: 月报）
            date: 报告日期（YYYYMMDD格式），如果不提供则使用今天

        Returns:
            报告数据
        """
        if not sn:
            raise XpyunError("打印机编号不能为空")

        if date is None:
            date = datetime.now().strftime('%Y%m%d')

        # 根据报告类型计算日期范围
        if report_type == "daily":
            end_date = date
            start_date = date
        elif report_type == "weekly":
            end = datetime.strptime(date, '%Y%m%d')
            start = end - timedelta(days=6)
            start_date = start.strftime('%Y%m%d')
            end_date = end.strftime('%Y%m%d')
        elif report_type == "monthly":
            current = datetime.strptime(date[:6] + '01', '%Y%m%d')
            start_date = current.strftime('%Y%m%d')

            # 获取下个月的第一天，然后减去一天
            if current.month == 12:
                next_month = current.replace(year=current.year + 1, month=1)
            else:
                next_month = current.replace(month=current.month + 1)
            end_date = (next_month - timedelta(days=1)).strftime('%Y%m%d')
        else:
            raise XpyunError(f"不支持的报告类型: {report_type}")

        # 获取统计数据
        statistics = self.get_order_statistics(sn, start_date, end_date)

        return {
            "report_type": report_type,
            "date_range": {
                "start": start_date,
                "end": end_date
            },
            "statistics": statistics,
            "summary": self._generate_report_summary(statistics, report_type)
        }

    def _generate_report_summary(self, statistics: Dict[str, Any], report_type: str) -> str:
        """
        生成报告摘要

        Args:
            statistics: 统计数据
            report_type: 报告类型

        Returns:
            报告摘要文本
        """
        total_orders = statistics.get("print_orders", 0)
        failed_orders = statistics.get("failed_orders", 0)
        success_rate = statistics.get("success_rate", 0)

        if report_type == "daily":
            return f"今日订单统计：共 {total_orders} 单，成功 {total_orders - failed_orders} 单，成功率 {success_rate}%"
        elif report_type == "weekly":
            avg_orders = total_orders / 7
            return f"本周订单统计：共 {total_orders} 单，日均 {avg_orders:.1f} 单，成功率 {success_rate}%"
        elif report_type == "monthly":
            avg_orders = total_orders / 30  # 近似计算
            return f"本月订单统计：共 {total_orders} 单，日均 {avg_orders:.1f} 单，成功率 {success_rate}%"
        else:
            return ""

    def format_duration(self, seconds: int) -> str:
        """
        格式化时长

        Args:
            seconds: 秒数

        Returns:
            格式化后的时长字符串
        """
        if seconds < 60:
            return f"{seconds}秒"
        elif seconds < 3600:
            minutes = seconds // 60
            secs = seconds % 60
            return f"{minutes}分{secs}秒"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours}小时{minutes}分"

    def is_business_hours(self, hours_start: int = 9, hours_end: int = 21) -> bool:
        """
        判断是否营业时间内

        Args:
            hours_start: 营业开始时间（小时）
            hours_end: 营业结束时间（小时）

        Returns:
            True表示在营业时间内
        """
        now = datetime.now()
        return hours_start <= now.hour < hours_end