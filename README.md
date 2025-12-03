# 芯烨云打印机SDK (XPYUN SDK)

芯烨云打印机SDK for Python，提供远程小票/标签订单打印、状态查询、语音播报等SaaS服务。

## 功能特性

- 🔥 完整的API覆盖 - 支持所有芯烨云开放API
- 📱 简单易用 - 面向对象的Python SDK设计
- 🎯 模块化架构 - 分离的服务模块（打印、查询、语音）
- 🚀 批量操作 - 支持批量打印和批量打印机管理
- 🔧 错误处理 - 完善的异常处理机制
- 🎨 格式化输出 - 自动格式化小票和标签内容
- 📞 语音播报 - 支持多种语言的收款语音播报
- 📊 统计报告 - 订单统计和日报/周报/月报生成

## 快速开始

### 安装

```bash
pip install xpyun-sdk
```

### 基本使用

```python
from xpyun_sdk import XpyunClient

# 初始化客户端
client = XpyunClient(
    user="your_user_id",      # 用户ID
    user_key="your_user_key"  # 用户密钥
)

# 添加打印机
client.add_printers([{
    "sn": "123456789012",
    "name": "前台打印机"
}])

# 打印小票
content = """
**订单信息**
订单号: 0012345678
时间: 2024-01-01 12:00
----------------------
商品A x2  20.00
商品B x1  15.00
----------------------
合计: 35.00元
"""

result = client.print_ticket(sn="123456789012", content=content)
print("打印成功，订单ID:", result.get("data"))
```

## 服务模块详解

### 1. 打印机管理 (PrinterManager)

```python
from xpyun_sdk.printer_manager import PrinterManager

printer_manager = PrinterManager(client)

# 添加打印机
printer_manager.add_printer(sn="123456789012", name="前台打印机")

# 删除打印机
printer_manager.delete_printer(sn="123456789012")

# 获取打印机状态
status = printer_manager.get_printer_status("123456789012")
print("打印机在线状态:", status.get("is_online"))
```

### 2. 打印服务 (PrintService)

```python
from xpyun_sdk.print_service import PrintService

print_service = PrintService(client)

# 打印格式化的小票
order_data = {
    "title": "点餐单",
    "order_no": "ORD20240001",
    "time": "2024-01-01 12:30:00",
    "table_no": "1号桌",
    "items": [
        {"name": "红烧肉", "qty": 1, "price": 28.0},
        {"name": "凉拌黄瓜", "qty": 1, "price": 15.0}
    ],
    "remark": "不要加辣",
    "total_amount": 43.0
}

print_service.print_order(
    sn="123456789012",
    order_data=order_data,
    order_type="receipt",
    copies=1,
    voice_enabled=True
)

# 打印标签
print_service.print_label(
    sn="123456789012",
    content="商品名称: 新鲜苹果\n价格: ￥8.80\n规格: 500g",
    height=40,
    width=30,
    quantity=10
)
```

### 3. 语音服务 (VoiceService)

```python
from xpyun_sdk.voice_service import VoiceService

voice_service = VoiceService(client)

# 设置语音类型
voice_service.set_voice_type(
    sn="123456789012",
    voice_type="MANDARIN_FEMALE",
    voice_enabled=True
)

# 播放收款语音
voice_service.play_amount_voice(
    sn="123456789012",
    amount=88.8,
    pay_type="CASH"  # 也可以是 "CARD", "QR_CODE"
)

# 语音播报新订单
voice_service.play_new_order_voice("123456789012")
```

### 4. 查询服务 (QueryService)

```python
from xpyun_sdk.query_service import QueryService

query_service = QueryService(client)

# 获取订单统计
stats = query_service.get_order_statistics(
    sn="123456789012",
    days=7  # 最近7天
)
print("订单统计:", stats)

# 生成报告
report = query_service.generate_report(
    sn="123456789012",
    report_type="weekly"  # daily, weekly, monthly
)
print("报告摘要:", report.get("summary"))

# 检查打印机状态
is_online = query_service.is_printer_online("123456789012")
print("打印机在线:", "是" if is_online else "否")
```

## 高级功能

### 批量操作

```python
# 批量添加打印机
printer_manager.add_printers([
    {"sn": "123456789011", "name": "总店"},
    {"sn": "123456789012", "name": "分店1"},
    {"sn": "123456789013", "name": "分店2"}
])

# 批量打印
batch_tasks = [
    {"sn": "123456789012", "content": "订单1", "copies": 1},
    {"sn": "123456789012", "content": "订单2", "copies": 2},
    {"sn": "123456789012", "content": "标签1", "height": 50, "quantity": 5}
]

results = print_service.batch_print(batch_tasks)
for i, result in enumerate(results):
    print(f"任务{i+1}: {'成功' if result['success'] else '失败'}")
```

### 自定义格式化

```python
# 自定义小票格式
def custom_receipt_formatter(order_data):
    lines = []
    lines.append(f"**{order_data.get('shop_name', '商店')}**")
    lines.append(f"订单号: {order_data['order_id']}")
    lines.append(f"时间: {order_data['timestamp']}")
    lines.append("="*20)

    for item in order_data['items']:
        lines.append(f"{item['name']:15} ¥{item['price']:6.2f}")

    lines.append("="*20)
    lines.append(f"总计: ¥{order_data['total']:.2f}")
    lines.append(f"支付: {order_data['payment_method']}")
    lines.append(order_data.get('footer', '感谢您的光临'))

    return "\n".join(lines)

# 使用自定义格式化
content = custom_receipt_formatter({
    'shop_name': '我的小店',
    'order_id': 'ORD20240001',
    'timestamp': '2024-01-01 12:00:00',
    'items': [{'name': '商品A', 'price': 15.50}],
    'total': 15.50,
    'payment_method': '微信支付'
})

print_service.print_receipt(
    sn="123456789012",
    content=content,
    copies=1
)
```

## 错误处理

```python
from xpyun_sdk import XpyunClient, XpyunError, XpyunAuthError, XpyunAPIError

try:
    result = client.print_ticket("123456789012", "测试内容")

except XpyunAuthError as e:
    print("认证失败 - 请检查用户ID和密钥")
    print(f"错误详情: {e}")

except XpyunAPIError as e:
    print(f"API错误 - 错误码: {e.code}, 错误消息: {e.message}")

    if e.code == 1:
        print("用户不存在")
    elif e.code == 2:
        print("参数错误")
    elif e.code == 3:
        print("打印机不存在")
    elif e.code == 4:
        print("打印内容超长")

except XpyunError as e:
    print(f"SDK错误: {e}")

except Exception as e:
    print(f"未知错误: {e}")
```

## API参考

### 主要接口

| 模块 | 方法 | 描述 |
|-----|-----|------|
| `XpyunClient` | `print_ticket()` | 打印小票 |
| `XpyunClient` | `print_label()` | 打印标签 |
| `XpyunClient` | `add_printers()` | 添加打印机 |
| `XpyunClient` | `query_order_state()` | 查询订单状态 |
| `PrintService` | `print_order()` | 格式化打印订单 |
| `PrintService` | `batch_print()` | 批量打印 |
| `PrinterManager` | `get_printer_status()` | 获取打印机状态 |
| `VoiceService` | `play_amount_voice()` | 播放收款语音 |
| `QueryService` | `generate_report()` | 生成统计报告 |

### 语音类型

```python
VoiceService.VOICE_TYPES = {
    "MANDARIN_FEMALE": 0,      # 中文女声
    "MANDARIN_MALE": 1,        # 中文男声
    "CANTONESE_FEMALE": 2,     # 粤语女声
    "ENGLISH_FEMALE": 3,       # 英文女声
    "CANTONESE_MALE": 4,       # 粤语男声
    "ENGLISH_MALE": 5,         # 英文男声
}
```

### 支付类型

```python
VoiceService.PAY_TYPES = {
    "CASH": 1,      # 现金
    "CARD": 2,      # 银行卡
    "QR_CODE": 3,   # 扫码支付
    "OTHER": 0,     # 其他
}
```

## 完整示例

运行示例程序需要配置您的用户ID和密钥：

```python
python example.py   # 显示所有示例菜单
python example.py 1  # 运行基础使用示例
python example.py 2  # 运行服务模块示例
python example.py 3  # 运行高级功能示例
python example.py 4  # 运行错误处理示例
```

## 调试模式

开启调试模式查看详细的API请求和响应：

```python
client = XpyunClient(
    user="your_user_id",
    user_key="your_user_key",
    debug=True  # 开启调试模式
)
```

## 环境要求

- Python 3.8+
- requests >= 2.25.0

## 注意事项

1. **用户认证**: 使用前请确保您已在芯烨云平台注册并获取了 `user` 和 `user_key`
2. **打印机编号**: 打印机的 `sn` 必须是在芯烨云平台已绑定的设备
3. **内容长度**: 打印内容长度限制请参考芯烨云官方文档
4. **网络连接**: 确保网络畅通，所有API调用都是网络请求
5. **错误处理**: 生产环境中务必完善错误处理机制


- API文档: https://www.xpyun.net/open/index.html
- SDK问题反馈: 请在GitHub提交Issue
