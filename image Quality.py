# -*- coding: utf-8 -*-
from airtest.core.api import *
from poco.drivers.android.uiautomation import AndroidUiautomationPoco
import time
import json
import requests
import os
import sys
import datetime
import re
import base64
import codecs

# 修改程序的輸出編碼格式。首先，通過調用 codecs.getwriter 函數，創建一個使用 UTF-8 編碼的輸出流。然後，通過調用 sys.stdout.detach 方法，獲取標準輸出流的低層接口。最後，將新創建的輸出流賦值給 sys.stdout，以替換標準輸出流。這樣，程序的所有輸出都將使用 UTF-8 編碼。
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

# 初始化Airtest
auto_setup(__file__)

# 初始化Poco
poco = AndroidUiautomationPoco(use_airtest_input=True, screenshot_each_action=False)

web = "com.photogrid.collage.videomaker"
xy = poco.get_screen_size()  # 获取手机屏幕尺寸
x = xy[0]  # X
y = xy[1]  # Y

# 定义发送信息函数
def send_message(message):
    bot_url = 'https://open.feishu.cn/open-apis/bot/v2/hook/d732dee1-df80-4ff6-9e12-87eea731ed5d'  # 主要群組
#     bot_url = 'https://open.feishu.cn/open-apis/bot/v2/hook/12196b5f-51f8-4d15-b744-0bd3be07cd13'  # 測試機器人
    headers = {'Content-Type': 'application/json'}
    data = {
        "msg_type": "text",
        "content": {
            "text": message
        }
    }
    response = requests.post(bot_url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        print("訊息已成功傳送到飛書機器人群組")
    else:
        print("傳送訊息到飛書機器人群組時發生錯誤")

# 清除数据
# clear_app(package=web)
# 关闭app
stop_app(package=web)
# 开启app
start_app(package=web)

sleep(5.0)

# 看是否在首页, 是的话开始进行超清画质
if poco(text="超清畫質").exists():
    poco(text="超清畫質").click()
    poco("android.widget.FrameLayout").child("android.widget.LinearLayout").offspring(
        "com.photogrid.collage.videomaker:id/page_root").offspring(
        "com.photogrid.collage.videomaker:id/selector_layout").offspring(
        "com.photogrid.collage.videomaker:id/grid_container").offspring(
        "com.photogrid.collage.videomaker:id/pic_grid").child("android.widget.RelativeLayout")[0].child(
        "com.photogrid.collage.videomaker:id/grid_image").click()
else:
    print("沒看到超清畫質按鈕")

sleep(3.0)

if poco(text="網絡錯誤，請再試一次。").exists():
    # 构建消息
    message_body = '超清畫質失敗\n錯誤提示:網路錯誤\n請檢查測試機網路狀態'
    # 发送结果到飞书机器人群组
    send_message(message_body)
    poco(text="確認").click()

# 等待目标字符串出现
target_string = "照片增強需要幾秒，請不要退出應用程序"  # 替换为要等待的字符串
poco(text=target_string).wait_for_appearance()
start_time = time.time()  # 记录开始时间
# 如果字符串出现，将继续执行后续代码
print("開始進行超清畫質！")

# 循环检查目标字符串是否存在，直到它消失或经过了120秒
sent_60s_message = False
operation_completed = False

while poco(text=target_string).exists():
    elapsed_time = time.time() - start_time

    # 如果经过的时间超过60秒但未发送消息，则发送消息
    if elapsed_time >= 60 and not sent_60s_message:
        print("已經達到60秒，發送訊息")
#         message_body = f'超清畫質\n等待時間超過60秒'
#         send_message(message_body)
        sent_60s_message = True

    # 如果经过的时间超过60秒，则中断循环
    if elapsed_time >= 60:
        print("已經達到60秒，中斷循環")
        poco(text="取消").click()
        break

    # 每隔1秒检查一次
    time.sleep(1)

# 目标字符串消失后停止计时，并计算存在时间
if not poco(text=target_string).exists():
    operation_completed = True

end_time = time.time()  # 记录结束时间
duration = end_time - start_time  # 计算存在时间

sleep(3.0)

if poco(text="網絡錯誤，請再試一次。").exists():
    # 构建消息
    message_body = '超清畫質失效\n錯誤提示:網路錯誤\n請檢查測試機網路'

    # 发送结果到飞书机器人群组
    send_message(message_body)

# 检查是否超过一分钟
if duration > 60:
    print("超過60秒")
    # 构建消息
    message_body = f'超清畫質\n等待時間超過60秒'
    # 发送结果到飞书机器人群组
    send_message(message_body)
    # 第二次执行
    print("開始第二次執行")
    # 重新初始化Airtest
    auto_setup(__file__)
    # 重新初始化Poco
    poco = AndroidUiautomationPoco(use_airtest_input=True, screenshot_each_action=False)
    # 关闭并重新启动app
    stop_app(package=web)
    start_app(package=web)
    sleep(5.0)
    # 重新执行步骤
    if poco(text="超清畫質").exists():
        poco(text="超清畫質").click()
        poco("android.widget.FrameLayout").child("android.widget.LinearLayout").offspring(
            "com.photogrid.collage.videomaker:id/page_root").offspring(
            "com.photogrid.collage.videomaker:id/selector_layout").offspring(
            "com.photogrid.collage.videomaker:id/grid_container").offspring(
            "com.photogrid.collage.videomaker:id/pic_grid").child("android.widget.RelativeLayout")[0].child(
            "com.photogrid.collage.videomaker:id/grid_image").click()
    else:
        print("沒看到超清畫質按鈕")
    sleep(3.0)
    if poco(text="網絡錯誤，請再試一次。").exists():
        # 构建消息
        message_body = '超清畫質第二次執行失敗\n錯誤提示:網路錯誤\n請檢查測試機網路'
        # 发送结果到飞书机器人群组
        send_message(message_body)
        poco(text="確認").click()
    # 等待目标字符串出现
    target_string = "照片增強需要幾秒，請不要退出應用程序"
    poco(text=target_string).wait_for_appearance()
    start_time = time.time()
    print("開始第二次超清畫質！")
    # 循环检查目标字符串是否存在，直到它消失或经过120秒
    sent_60s_message = False
    while poco(text=target_string).exists():
        elapsed_time = time.time() - start_time
        if elapsed_time >= 30 and not sent_60s_message:
            print("已經達到30秒，發送訊息")
#             message_body = f'超清畫質第二次執行\n等待時間超過60秒'
#             send_message(message_body)
            sent_60s_message = True
        if elapsed_time >= 90:
            print("已經達到90秒，中斷循環")
            poco(text="取消").click()
            break
        time.sleep(1)
    if not poco(text=target_string).exists():
        operation_completed = True
    end_time = time.time()
    duration = end_time - start_time
    sleep(3.0)
    if poco(text="網絡錯誤，請再試一次。").exists():
        # 构建消息
        message_body = '超清畫質第二次執行失敗\n錯誤提示:網路錯誤\n請檢查測試機網路'
        # 发送结果到飞书机器人群组
        send_message(message_body)
    if duration > 90:
        print("超過90秒")
        message_body = f'【加急加急加急】\n超清畫質第二次執行\n等待時間超過90秒,請QA手動測試目前狀況'
        send_message(message_body)
    else:
        print(f"超清畫質第二次執行完成！回傳時間為：{duration:.2f}秒")
else:
    print(f"超清畫質完成！回傳時間為：{duration:.2f}秒")

