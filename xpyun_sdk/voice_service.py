"""
语音服务模块
提供语音播报相关功能
"""

from typing import Dict, Any, Optional, List
import time
from .client import XpyunClient
from .exceptions import XpyunError


class VoiceService:
    """语音服务"""

    # 语音类型定义
    VOICE_TYPES = {
        "MANDARIN_FEMALE": 0,      # 中文女声
        "MANDARIN_MALE": 1,        # 中文男声
        "CANTONESE_FEMALE": 2,     # 粤语女声
        "ENGLISH_FEMALE": 3,       # 英文女声
        "CANTONESE_MALE": 4,       # 粤语男声
        "ENGLISH_MALE": 5,         # 英文男声
    }

    # 支付类型定义
    PAY_TYPES = {
        "CASH": 1,                  # 现金支付
        "CARD": 2,                  # 银行卡支付
        "QR_CODE": 3,               # 扫码支付
        "OTHER": 0,                 # 其他支付
    }

    def __init__(self, client: XpyunClient):
        """
        初始化语音服务

        Args:
            client: xpyun客户端实例
        """
        self.client = client

    def set_voice_type(self, sn: str, voice_type: int or str, voice_enabled: bool = True) -> Dict[str, Any]:
        """
        设置语音类型

        Args:
            sn: 打印机编号
            voice_type: 语音类型（数字或预设字符串）
            voice_enabled: 是否启用语音播报

        Returns:
            API响应数据
        """
        if not sn:
            raise XpyunError("打印机编号不能为空")

        # 转换语音类型
        if isinstance(voice_type, str):
            voice_type_int = self.VOICE_TYPES.get(voice_type.upper())
            if voice_type_int is None:
                raise XpyunError(f"不支持的语音类型: {voice_type}")
        else:
            voice_type_int = voice_type

        return self.client.set_voice_type(sn, voice_type_int, 1 if voice_enabled else 0)

    def play_voice(self, sn: str, voice_type: str, pay_type: int or str = None) -> Dict[str, Any]:
        """
        播放语音

        Args:
            sn: 打印机编号
            voice_type: 语音类型（字符串）
            pay_type: 支付类型（可选）

        Returns:
            API响应数据
        """
        if not sn or not voice_type:
            raise XpyunError("打印机编号和语音类型不能为空")

        # 转换支付类型
        if pay_type is not None:
            if isinstance(pay_type, str):
                pay_type_int = self.PAY_TYPES.get(pay_type.upper())
                if pay_type_int is None:
                    raise XpyunError(f"不支持的支付类型: {pay_type}")
            else:
                pay_type_int = pay_type
        else:
            pay_type_int = None

        return self.client.play_voice(sn, voice_type, pay_type_int)

    def play_amount_voice(self, sn: str, amount: float, pay_type: str = "CASH") -> Dict[str, Any]:
        """
        播放收款金额语音

        Args:
            sn: 打印机编号
            amount: 金额
            pay_type: 支付类型

        Returns:
            API响应数据
        """
        # 格式化金额语音
        amount_str = self._format_amount_voice(amount)
        voice_type = f"AMOUNT_{pay_type.upper()}"

        return self.play_voice(sn, voice_type, pay_type)

    def play_welcome_message(self, sn: str, voice_type: str = "MANDARIN_FEMALE") -> Dict[str, Any]:
        """
        播放欢迎语音

        Args:
            sn: 打印机编号
            voice_type: 语音类型

        Returns:
            API响应数据
        """
        return self.play_voice(sn, f"WELCOME_{voice_type}")

    def print_and_voice(self, sn: str, content: str, amount: float = None,
                       voice_enabled: bool = True, pay_type: str = "CASH") -> Dict[str, Any]:
        """
        打印并播报

        Args:
            sn: 打印机编号
            content: 打印内容
            amount: 金额（如果有）
            voice_enabled: 是否启用语音播报
            pay_type: 支付类型

        Returns:
            打印结果
        """
        from .print_service import PrintService

        print_service = PrintService(self.client)

        # 执行打印
        print_result = print_service.print_receipt(
            sn=sn,
            content=content,
            voice_enabled=voice_enabled
        )

        # 如果需要播报金额
        if voice_enabled and amount is not None:
            try:
                self.play_amount_voice(sn, amount, pay_type)
            except Exception as e:
                print(f"语音播报失败: {e}")

        return print_result

    def voice_auto_order(self, sn: str, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        根据订单数据自动生成语音播报

        Args:
            sn: 打印机编号
            order_data: 订单数据

        Returns:
            API响应数据
        """
        amount = order_data.get('total_amount')
        pay_type = order_data.get('pay_type', 'CASH')

        # 如果有金额，先播报收款语音
        if amount is not None:
            try:
                self.play_amount_voice(sn, amount, pay_type)
                time.sleep(1)  # 暂停1秒
            except Exception as e:
                print(f"金额语音播报失败: {e}")

        # 播报订单内容（如果有新订单语音）
        try:
            return self.play_voice(sn, "NEW_ORDER")
        except Exception as e:
            print(f"订单语音播报失败: {e}")
            return None

    def set_auto_voice_mode(self, sn: str, voice_type: str = "MANDARIN_FEMALE",
                           voice_contents: List[str] = None) -> Dict[str, Any]:
        """
        设置自动语音模式

        Args:
            sn: 打印机编号
            voice_type: 语音类型
            voice_contents: 需要自动播报的内容类型列表

        Returns:
            API响应数据
        """
        if voice_contents is None:
            voice_contents = ["NEW_ORDER", "COMPLETE_ORDER", "ERROR"]

        # 设置语音类型
        result = self.set_voice_type(sn, voice_type)

        # TODO: 需要云平台支持保存自动语音配置
        # 这里可以添加保存本地配置的逻辑

        return {
            "voice_type_set": result,
            "auto_voice_contents": voice_contents,
            "message": f"已设置{voice_type}语音类型，自动播报模式已启用"
        }

    def disable_all_voices(self, sn: str) -> Dict[str, Any]:
        """
        禁用所有语音播报

        Args:
            sn: 打印机编号

        Returns:
            API响应数据
        """
        return self.set_voice_type(sn, 0, False)

    def test_voice(self, sn: str, voice_type: str = "MANDARIN_FEMALE") -> Dict[str, Any]:
        """
        测试语音播报

        Args:
            sn: 打印机编号
            voice_type: 语音类型

        Returns:
            API响应数据
        """
        return self.play_voice(sn, f"TEST_{voice_type}")

    def _format_amount_voice(self, amount: float) -> str:
        """
        格式化金额语音

        Args:
            amount: 金额

        Returns:
            格式化后的金额语音字符串
        """
        # 将金额转换为中文语音格式
        # 例如：25.8 -> "二十五元八角"
        amount_str = str(amount)

        # 这里需要根据实际的语音播报格式来格式化
        # 目前返回原格式，实际需要配合云平台的具体要求
        return amount_str

    def get_voice_settings(self, sn: str) -> Dict[str, Any]:
        """
        获取语音设置信息

        Args:
            sn: 打印机编号

        Returns:
            语音设置信息
        """
        # 获取打印机状态来分析语音设置
        status = self.client.query_printer_status(sn)

        data = status.get("data", {})

        return {
            "is_voice_enabled": data.get("voiceEnabled", False),
            "current_voice_type": data.get("voiceType", 0),
            "voice_quality": data.get("voiceQuality", "normal"),
            "last_voice_update": data.get("lastVoiceUpdate"),
            "supported_voices": list(self.VOICE_TYPES.keys())
        }

    def validate_voice_support(self, sn: str) -> bool:
        """
        验证打印机是否支持语音功能

        Args:
            sn: 打印机编号

        Returns:
            True表示支持语音功能
        """
        settings = self.get_voice_settings(sn)
        return settings.get("voice_quality") is not None

    # 预定义的语音类型快捷方法
    def play_chinese_female(self, sn: str, message_type: str, **kwargs) -> Dict[str, Any]:
        """播放中文女声"""
        return self.play_voice(sn, f"FEMALE_{message_type}", **kwargs)

    def play_chinese_male(self, sn: str, message_type: str, **kwargs) -> Dict[str, Any]:
        """播放中文男声"""
        return self.play_voice(sn, f"MALE_{message_type}", **kwargs)

    def play_cantonese(self, sn: str, message_type: str, is_female: bool = True, **kwargs) -> Dict[str, Any]:
        """播放粤语"""
        gender = "FEMALE" if is_female else "MALE"
        return self.play_voice(sn, f"CANTONESE_{gender}_{message_type}", **kwargs)

    def play_english(self, sn: str, message_type: str, is_female: bool = True, **kwargs) -> Dict[str, Any]:
        """播放英文"""
        gender = "FEMALE" if is_female else "MALE"
        return self.play_voice(sn, f"ENGLISH_{gender}_{message_type}", **kwargs)

    # 常用业务语音快捷方法
    def play_new_order_voice(self, sn: str, voice_type: str = "FEMALE") -> Dict[str, Any]:
        """播放新订单语音"""
        return self.play_voice(sn, f"{voice_type}_NEW_ORDER")

    def play_complete_order_voice(self, sn: str, voice_type: str = "FEMALE") -> Dict[str, Any]:
        """播放订单完成语音"""
        return self.play_voice(sn, f"{voice_type}_COMPLETE_ORDER")

    def play_error_voice(self, sn: str, voice_type: str = "FEMALE") -> Dict[str, Any]:
        """播放错误语音"""
        return self.play_voice(sn, f"{voice_type}_ERROR")

    def play_no_paper_voice(self, sn: str, voice_type: str = "FEMALE") -> Dict[str, Any]:
        """播放缺纸语音"""
        return self.play_voice(sn, f"{voice_type}_NO_PAPER")

    def play_low_battery_voice(self, sn: str, voice_type: str = "FEMALE") -> Dict[str, Any]:
        """播放低电量语音"""
        return self.play_voice(sn, f"{voice_type}_LOW_BATTERY")