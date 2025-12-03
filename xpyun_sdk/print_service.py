"""
打印服务模块
提供小票和标签打印功能
"""

from typing import Dict, Any, Optional, List
from .client import XpyunClient
from .exceptions import XpyunError


class PrintService:
    """打印服务"""

    def __init__(self, client: XpyunClient):
        """
        初始化打印服务

        Args:
            client: xpyun客户端实例
        """
        self.client = client

    def print_receipt(self,
                     sn: str,
                     content: str,
                     copies: int = 1,
                     code_u: str = "",
                     auto_print: bool = True,
                     voice_enabled: bool = False) -> Dict[str, Any]:
        """
        打印小票

        Args:
            sn: 打印机编号
            content: 打印内容
            copies: 打印份数（1-10）
            code_u: 更新编号（用于更新打印内容）
            auto_print: 是否自动打印（True: 自动，False: 强制）
            voice_enabled: 是否启用语音播报

        Returns:
            API响应数据，包含订单ID
        """
        if not sn or not content:
            raise XpyunError("打印机编号和内容不能为空")

        if copies < 1 or copies > 10:
            raise XpyunError("打印份数必须在1-10之间")

        mode = 0 if auto_print else 1
        voice = 1 if voice_enabled else 0

        return self.client.print_ticket(
            sn=sn,
            content=content,
            times=copies,
            code_u=code_u,
            mode=mode,
            voice=voice
        )

    def print_label(self,
                   sn: str,
                   content: str,
                   height: int,
                   width: int = 30,
                   quantity: int = 1,
                   top_margin: int = 0,
                   left_margin: int = 0,
                   code_u: str = "") -> Dict[str, Any]:
        """
        打印标签

        Args:
            sn: 打印机编号
            content: 标签内容
            height: 标签高度（毫米）
            width: 标签宽度（毫米）
            quantity: 打印数量
            top_margin: 上边距（毫米）
            left_margin: 左边距（毫米）
            code_u: 更新编号（用于更新打印内容）

        Returns:
            API响应数据，包含订单ID
        """
        if not sn or not content:
            raise XpyunError("打印机编号和内容不能为空")

        if height <= 0 or width <= 0:
            raise XpyunError("标签高度和宽度必须是正数")

        if quantity < 1 or quantity > 100:
            raise XpyunError("打印数量必须在1-100之间")

        return self.client.print_label(
            sn=sn,
            content=content,
            height=height,
            width=width,
            quantity=quantity,
            top=top_margin,
            left=left_margin,
            code_u=code_u
        )

    def print_order(self,
                   sn: str,
                   order_data: Dict[str, Any],
                   order_type: str = "receipt",
                   **kwargs) -> Dict[str, Any]:
        """
        打印订单信息

        Args:
            sn: 打印机编号
            order_data: 订单数据
            order_type: 订单类型（receipt: 小票，label: 标签）
            **kwargs: 其他打印参数

        Returns:
            API响应数据
        """
        if order_type == "receipt":
            content = self._format_receipt_content(order_data)
            return self.print_receipt(sn, content, **kwargs)
        elif order_type == "label":
            content = self._format_label_content(order_data)
            height = kwargs.pop('height', 50)  # 默认高度50mm
            return self.print_label(sn, content, height, **kwargs)
        else:
            raise XpyunError(f"不支持的订单类型: {order_type}")

    def batch_print(self,
                   print_tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        批量打印

        Args:
            print_tasks: 打印任务列表，每个任务包含sn、content等参数

        Returns:
            打印结果列表
        """
        results = []
        for task in print_tasks:
            try:
                if 'content' in task:
                    # 小票打印
                    result = self.print_receipt(**task)
                elif 'order_data' in task:
                    # 订单打印
                    result = self.print_order(**task)
                else:
                    # 标签打印
                    result = self.print_label(**task)

                results.append({
                    "success": True,
                    "data": result,
                    "task": task
                })
            except Exception as e:
                results.append({
                    "success": False,
                    "error": str(e),
                    "task": task
                })

        return results

    def _format_receipt_content(self, order_data: Dict[str, Any]) -> str:
        """
        格式化小票内容

        Args:
            order_data: 订单数据

        Returns:
            格式化后的小票内容
        """
        # 基本信息
        content = []

        # 标题
        content.append(f"**{order_data.get('title', '订单详情')}**")
        content.append("----------------------")

        # 订单信息
        content.append(f"订单号: {order_data.get('order_no', '')}")
        content.append(f"时间: {order_data.get('time', '')}")
        content.append(f"桌号: {order_data.get('table_no', '')}")
        content.append("")

        # 商品列表
        content.append("**商品清单**")
        content.append("----------------------")

        items = order_data.get('items', [])
        for item in items:
            name = item.get('name', '')
            qty = item.get('qty', 0)
            price = item.get('price', 0)
            amount = item.get('amount', qty * price)
            content.append(f"{name} x{qty}  {amount:.2f}")

        content.append("----------------------")

        # 统计信息
        total_quantity = sum(item.get('qty', 0) for item in items)
        total_amount = sum(item.get('amount', item.get('qty', 0) * item.get('price', 0)) for item in items)

        content.append(f"合计: {total_quantity}件  ￥{total_amount:.2f}")
        content.append(f"应付: ￥{order_data.get('total_amount', total_amount):.2f}")

        # 备注
        if order_data.get('remark'):
            content.append("")
            content.append(f"备注: {order_data.get('remark')}")

        content.append("")
        content.append(order_data.get('footer', '谢谢惠顾，欢迎下次光临！'))

        return "\n".join(content)

    def _format_label_content(self, label_data: Dict[str, Any]) -> str:
        """
        格式标签内容

        Args:
            label_data: 标签数据

        Returns:
            格式化后的标签内容
        """
        content = []

        # 商品名称
        content.append(f"**{label_data.get('product_name', '商品') }**")
        content.append("")

        # 条码
        if label_data.get('barcode'):
            content.append(f"条码: {label_data.get('barcode')}")

        # 价格
        if label_data.get('price') is not None:
            price = float(label_data.get('price'))
            content.append(f"价格: ￥{price:.2f}")

        # 规格
        if label_data.get('spec'):
            content.append(f"规格: {label_data.get('spec')}")

        # 生产日期
        if label_data.get('production_date'):
            content.append(f"生产日期: {label_data.get('production_date')}")

        # 保质期
        if label_data.get('expiry_date'):
            content.append(f"保质期: {label_data.get('expiry_date')}")

        # 其他自定义字段
        for key, value in label_data.items():
            if key not in ['product_name', 'barcode', 'price', 'spec', 'production_date', 'expiry_date']:
                content.append(f"{key}: {value}")

        return "\n".join(content)

    def create_test_receipt(self) -> str:
        """
        创建测试小票内容

        Returns:
            测试小票内容字符串
        """
        test_data = {
            "title": "测试订单",
            "order_no": "TEST001",
            "time": "2024-01-01 12:00:00",
            "table_no": "1号桌",
            "items": [
                {"name": "商品A", "qty": 2, "price": 10.00},
                {"name": "商品B", "qty": 1, "price": 15.00},
                {"name": "商品C", "qty": 3, "price": 8.00}
            ],
            "remark": "少放盐",
            "footer": "谢谢惠顾！"
        }
        return self._format_receipt_content(test_data)

    def create_test_label(self) -> str:
        """
        创建测试标签内容

        Returns:
            测试标签内容字符串
        """
        test_data = {
            "product_name": "测试商品",
            "barcode": "1234567890123",
            "price": 25.80,
            "spec": "500g/袋",
            "production_date": "2024-01-01",
            "expiry_date": "12个月"
        }
        return self._format_label_content(test_data)