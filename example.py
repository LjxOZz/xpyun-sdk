"""
芯烨云打印机SDK使用示例
"""

from xpyun_sdk import XpyunClient, XpyunError
from xpyun_sdk.printer_manager import PrinterManager
from xpyun_sdk.print_service import PrintService
from xpyun_sdk.voice_service import VoiceService
from xpyun_sdk.query_service import QueryService

def basic_usage():
    """基础使用示例"""

    # 初始化客户端
    client = XpyunClient(
        user="1911342262@qq.com",                       # 替换为您的用户ID
        user_key="eebc89e280ba47c5a12d6dc750348811",    # 替换为您的用户密钥
        debug=True                                      # 开启调试模式
    )

    try:
        # 添加打印机
        result = client.add_printers([{
            "sn": "36R0T38XWN71149",
            "name": "Selftest"
        }])
        print("添加打印机成功:", result)

        # 打印小票
        content = """
**订单信息**
订单号: 0012345678
时间: 2024-01-01 12:00
商品A x2  20.00
商品B x1  15.00
----------------------
合计: 3件  35.00元
**感谢您的光临**
"""

        print_result = client.print_ticket(
            sn="36R0T38XWN71149",
            content=content,
            times=1
        )
        print("打印小票成功，订单ID:", print_result.get("data"))

    except XpyunError as e:
        print(f"操作失败: {e}")

def service_usage():
    """使用服务模块的示例"""

    # 初始化客户端
    client = XpyunClient(
        user="your_user_id",
        user_key="your_user_key"
    )

    # 初始化各个服务模块
    printer_manager = PrinterManager(client)
    print_service = PrintService(client)
    voice_service = VoiceService(client)
    query_service = QueryService(client)

    try:
        sn = "36R0T38XWN71149"  # 您的打印机编号

        # 1. 打印机管理
        print("=== 打印机管理 ===")

        # 添加打印机
        printer_result = printer_manager.add_printer(
            sn=sn,
            name="测试打印机"
        )
        print("添加打印机结果:", printer_result)

        # 获取打印机状态
        status = printer_manager.get_printer_status(sn)
        print("打印机状态:", status)

        # 获取打印机详细信息
        info = printer_manager.get_printer_info(sn)
        print("打印机详细信息:", info)

        # 2. 打印服务
        print("\n=== 打印服务 ===")

        # 创建测试订单
        order_data = {
            "title": "点菜单",
            "order_no": "ORD20240001",
            "time": "2024-01-01 12:30:00",
            "table_no": "1号桌",
            "items": [
                {"name": "红烧肉", "qty": 1, "price": 28.0},
                {"name": "清蒸鲈鱼", "qty": 1, "price": 45.0},
                {"name": "青椒土豆丝", "qty": 1, "price": 18.0},
                {"name": "西红柿鸡蛋汤", "qty": 1, "price": 12.0}
            ],
            "remark": "不要加辣",
            "total_amount": 103.0
        }

        # 打印订单
        print_result = print_service.print_order(
            sn=sn,
            order_data=order_data,
            order_type="receipt",
            copies=1,
            voice_enabled=True
        )
        print("打印订单结果:", print_result)

        # 批量打印
        print("\n=== 批量打印 ===")
        batch_tasks = [
            {
                "sn": sn,
                "content": print_service.create_test_receipt(),
                "copies": 1
            },
            {
                "sn": sn,
                "content": print_service.create_test_label(),
                "height": 60,
                "width": 40,
                "quantity": 1
            }
        ]

        batch_results = print_service.batch_print(batch_tasks)
        print("批量打印结果:")
        for i, result in enumerate(batch_results):
            print(f"任务 {i+1}: {'成功' if result['success'] else '失败'}")
            if not result['success']:
                print(f"  错误: {result.get('error')}")

        # 3. 语音服务
        print("\n=== 语音服务 ===")

        # 设置语音类型
        voice_result = voice_service.set_voice_type(
            sn=sn,
            voice_type="MANDARIN_FEMALE",
            voice_enabled=True
        )
        print("设置语音类型结果:", voice_result)

        # 播放收款语音
        voice_result = voice_service.play_amount_voice(
            sn=sn,
            amount=88.8,
            pay_type="CASH"
        )
        print("播放收款语音结果:", voice_result)

        # 4. 查询服务
        print("\n=== 查询服务 ===")

        # 获取订单统计
        stats = query_service.get_order_statistics(sn, days=7)
        print("7天订单统计:", stats)

        # 生成报告
        report = query_service.generate_report(sn, "weekly")
        print("周报摘要:", report.get("summary"))

        # 检查打印机是否在线
        is_online = query_service.is_printer_online(sn)
        print(f"打印机在线状态: {'在线' if is_online else '离线'}")

    except XpyunError as e:
        print(f"操作失败: {e}")
        print(f"详细错误信息: {e.message if hasattr(e, 'message') else str(e)}")

def advanced_usage():
    """高级使用示例"""

    client = XpyunClient(
        user="your_user_id",
        user_key="your_user_key",
        debug=True  # 开启调试模式查看详细请求响应
    )

    sn = "36R0T38XWN71149"

    try:
        # 高级打印 - 自定义格式
        from xpyun_sdk.print_service import PrintService

        print_service = PrintService(client)

        # 餐厅订单格式
        restaurant_order = {
            "title": "**点餐单**",
            "order_no": f"R{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "table_no": "VIP包厢",
            "items": [
                {"name": "【招牌菜】水晶虾仁", "qty": 1, "price": 68},
                {"name": "【特色菜】东坡肘子", "qty": 1, "price": 128},
                {"name": "【时蔬】蒜蓉菜心", "qty": 1, "price": 25},
                {"name": "【汤品】西湖莼菜汤", "qty": 1, "price": 22}
            ],
            "remark": "客人对虾仁过敏，请特别注意",
            "footer": "感谢品尝，祝您用餐愉快！"
        }

        content = print_service._format_receipt_content(restaurant_order)
        print_result = print_service.print_receipt(
            sn=sn,
            content=content,
            copies=2,  # 打印两份，一份给厨房，一份给客人
            voice_enabled=True
        )

        print("餐厅订单打印成功")

        # 商品标签格式
        product_label = {
            "product_name": "【进口】新西兰奇异果",
            "barcode": "9400574012345",
            "price": 12.8,
            "spec": "单果100-120g",
            "origin": "新西兰",
            "production_date": "2024-01-01",
            "shelf_life": "15天",
            "storage_way": "冷藏保存"
        }

        label_content = print_service._format_label_content(product_label)
        label_result = print_service.print_label(
            sn=sn,
            content=label_content,
            height=50,  # 50mm高度
            width=30,   # 30mm宽度
            quantity=5, # 打印5张标签
            left_margin=2,
            top_margin=2
        )

        print("商品标签打印成功")

        # 批量多店铺管理
        print("\n=== 多店铺批量管理 ===")

        # 模拟多个商铺的打印机
        shops = [
            {"name": "总店", "sn": "123456789011"},
            {"name": "分店1", "sn": "36R0T38XWN71149"},
            {"name": "分店2", "sn": "123456789013"}
        ]

        for shop in shops:
            try:
                # 获取打印机状态
                status = client.query_printer_status(shop["sn"])
                print(f"{shop['name']} 状态: {status}")

                # 打印订单（如果在线）
                if status['data'].get('connected', False):
                    test_content = f"""
**{shop['name']} 测试订单**
订单号: TEST{shop['sn']}
时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
----------------------
测试商品 x1  10.00
----------------------
**测试完成**
"""
                    client.print_ticket(shop['sn'], test_content, times=1)
                    print(f"{shop['name']} 测试打印已发送")
                else:
                    print(f"{shop['name']} 打印机离线，跳過测试打印")

            except Exception as e:
                print(f"{shop['name']} 操作失败: {e}")

    except Exception as e:
        print(f"高级示例执行失败: {e}")

def error_handling_example():
    """错误处理示例"""

    client = XpyunClient(
        user="invalid_user",  # 错误的用户ID
        user_key="invalid_key"  # 错误的用户密钥
    )

    try:
        # 这将触发认证错误
        result = client.query_printer_status("123456789")
        print("这行不会被执行到")

    except XpyunError as e:
        print("捕获到基础异常:", e)

        # 可以区分不同类型的异常
        if hasattr(e, 'code'):
            print(f"API错误码: {e.code}")
            print(f"错误消息: {e.message}")

            # 根据错误码进行不同的处理
            if e.code == 1:
                print("用户不存在或密钥错误")
            elif e.code == 2:
                print("参数错误")
            elif e.code == 3:
                print("打印机不存在")
            # ... 其他错误码处理

    except Exception as e:
        print(f"未知异常: {e}")

if __name__ == "__main__":
    from datetime import datetime

    print("=== 芯烨云打印机SDK使用示例 ===\n")
    print("1. 基础使用示例")
    print("2. 服务模块使用示例")
    print("3. 高级使用示例")
    print("4. 错误处理示例")

    import sys
    if len(sys.argv) > 1:
        example_num = sys.argv[1]
    else:
        example_num = "2"

    if example_num == "1":
        basic_usage()
    elif example_num == "2":
        service_usage()
    elif example_num == "3":
        advanced_usage()
    elif example_num == "4":
        error_handling_example()
    else:
        print(f"不存在的示例: {example_num}")
        print("请使用: python example.py [1|2|3|4]")