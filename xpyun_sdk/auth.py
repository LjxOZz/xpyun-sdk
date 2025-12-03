"""
认证模块
实现SHA1签名认证
"""

import hashlib
import time
from typing import Dict, Optional


class XpyunAuth:
    """芯烨云认证类"""

    def __init__(self, user: str, user_key: str):
        """
        初始化认证

        Args:
            user: 用户ID
            user_key: 用户密钥
        """
        self.user = user
        self.user_key = user_key

    def generate_sign(self, timestamp: Optional[str] = None) -> str:
        """
        生成SHA1签名

        Args:
            timestamp: 时间戳，如果不提供则使用当前时间

        Returns:
            SHA1签名字符串（40位小写）
        """
        if timestamp is None:
            timestamp = str(int(time.time()))

        # 拼接字符串：user + UserKEY + timestamp
        sign_str = f"{self.user}{self.user_key}{timestamp}"

        # 计算SHA1哈希
        sha1_hash = hashlib.sha1(sign_str.encode('utf-8'))
        return sha1_hash.hexdigest().lower()

    def get_auth_params(self) -> Dict[str, str]:
        """
        获取认证参数

        Returns:
            包含user、timestamp、sign的字典
        """
        timestamp = str(int(time.time()))
        sign = self.generate_sign(timestamp)

        return {
            'user': self.user,
            'timestamp': timestamp,
            'sign': sign
        }
