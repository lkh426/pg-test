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

# 修改程序的輸出編碼格式
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

# 初始化Airtest
auto_setup(__file__)

# 初始化Poco
poco = AndroidUiautomationPoco(use_airtest_input=True, screenshot_each_action=False)

web = "com.photogrid.collage.videomaker"
xy = poco.get_screen_size()  # 获取手机屏幕尺寸
x = xy[0]  # X
y = xy[1]  # Y

# 定義發送訊息函數
def send_message(message):
    # bot_url = 'https://open.feishu.cn/open-apis/bot/v2/hook/d732dee1-df80-4ff6-9e12-87eea731ed5d'#朱比特账号机器人主要群組
    bot_url = 'https://open.feishu.cn/open-apis/bot/v2/hook/215772c2-3833-4996-9407-9ba67b8a1be4'#乐我机器人账号后
#     bot_url = 'https://open.feishu.cn/open-apis/bot/v2/hook/0a6ba36f-2dbb-41e8-92cb-ab9d93431d77'#測試機器人
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

# 清除資料
# clear_app(package=web)
# 關閉app
stop_app(package=web)
# 開啟app
start_app(package=web)

sleep(10.0)

swipe((1.0 * x, 0.165 * y), (0.25 * x, 0.165 * y))

one = 120
two = 120

# 看是否在首頁, 是的話開始進行AI重繪
if poco(text="AI重绘").exists():
    poco(text="AI重绘").click()
    sleep(2.0)
    poco(text="開始使用").click()
    poco("android.widget.FrameLayout").child("android.widget.LinearLayout").offspring(
        "com.photogrid.collage.videomaker:id/page_root").offspring(
        "com.photogrid.collage.videomaker:id/selector_layout").offspring(
        "com.photogrid.collage.videomaker:id/grid_container").offspring(
        "com.photogrid.collage.videomaker:id/pic_grid").child("android.widget.RelativeLayout")[0].child(
        "com.photogrid.collage.videomaker:id/grid_image").click()
    # 等待 "知道了！" 元素出現，並點擊它
    if poco(text="繼續").exists():
        poco(text="繼續").click()
    if poco(text="繼續").exists():
        poco(text="繼續").click()
    if poco(text="繼續").exists():
        poco(text="繼續").click()
    if poco(text="完成").exists():
        poco(text="完成").click()
    
    sleep(2.0)
#     poco(text="Normal").click()
    swipe((1.0 * x, 0.165 * y), (0.25 * x, 0.165 * y))
    sleep(1.0)
    poco(text="重繪此處").click()
    input_field = poco("com.photogrid.collage.videomaker:id/prompt")
    input_field.set_text("cat")
    poco(text="生成").click()

sleep(2.0)

if poco(text="稍後再試試吧！").exists():
    # 構建訊息
    message_body = 'AI重繪失敗\n錯誤提示:稍後再試試吧！\n請檢查測試機網路'
    # 發送結果到飛書機器人群組
    send_message(message_body)

if poco(text="無網路連線").exists():
    # 構建訊息
    message_body = 'AI重繪失敗\n錯誤提示:無網路連線\n請檢查測試機網路'
    # 發送結果到飛書機器人群組
    send_message(message_body)

# 等待目標字串出現
target_string = "com.photogrid.collage.videomaker:id/uploadingVideoAni"  # 將此處替換為你要等待的字串
poco(name=target_string).wait_for_appearance()
start_time = time.time()  # 記錄開始時間
# 如果字串出現，將繼續執行後續程式碼
print("開始進行AI重繪")

# 循環檢查目標字串是否存在，直到它消失或經過了120秒
sent_60s_message = False
operation_completed = False



while poco(name=target_string).exists():
    elapsed_time = time.time() - start_time

    # 打印已經經過的時間
    print(f"已經經過了 {elapsed_time:.2f} 秒")

    # 如果經過的時間超過60秒但未發送訊息，則發送訊息
    if elapsed_time >= 60 and not sent_60s_message:
#         print("已經達到60秒，發送訊息")
#         message_body = f'AI重繪\n等待時間超過60秒'
#         send_message(message_body)
        sent_60s_message = True

    # 如果經過的時間超過120秒，則中斷循環
    if elapsed_time >= one:
        print("已經達到120秒，中斷循環")
        stop_app(package=web)
        break

    # 每隔0.1秒檢查一次
    time.sleep(1)

# 目標字串消失後停止計時，並計算存在時間
if not poco(name=target_string).exists():
    operation_completed = True

end_time = time.time()  # 記錄結束時間
duration = end_time - start_time  # 計算存在時間

sleep(3.0)

if poco(text="網絡錯誤").exists():
    # 構建訊息
    message_body = 'AI重繪失敗\n錯誤提示:網路錯誤\n請檢查測試機網路'
    # 發送結果到飛書機器人群組
    send_message(message_body)

# 檢查是否超過兩分鐘
if duration > one:
    print("超過120秒")
    # 構建訊息
    message_body = f'AI重繪\n等待時間超過120秒'
    # 發送結果到飛書機器人群組
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
    if poco(text="AI重繪").exists():
        poco(text="AI重繪").click()
        sleep(2.0)
        poco(text="開始使用").click()
        poco("android.widget.FrameLayout").child("android.widget.LinearLayout").offspring(
            "com.photogrid.collage.videomaker:id/page_root").offspring(
            "com.photogrid.collage.videomaker:id/selector_layout").offspring(
            "com.photogrid.collage.videomaker:id/grid_container").offspring(
            "com.photogrid.collage.videomaker:id/pic_grid").child("android.widget.RelativeLayout")[0].child(
            "com.photogrid.collage.videomaker:id/grid_image").click()
        swipe((1.0 * x, 0.165 * y), (0.25 * x, 0.165 * y))
        sleep(1.0)
        poco(text="重繪此處").click()
        input_field = poco("com.photogrid.collage.videomaker:id/prompt")
        input_field.set_text("cat")
        poco(text="生成").click()
    else:
        print("首頁沒看到AI重繪入口")
    sleep(2.0)
    if poco(text="稍後再試試吧！").exists():
        # 構建訊息
        message_body = 'AI重繪第二次執行失敗\n錯誤提示:稍後再試試吧！\n請檢查測試機網路'
        # 發送結果到飛書機器人群組
        send_message(message_body)
    if poco(text="無網路連線").exists():
        # 構建訊息
        message_body = 'AI重繪第二次執行失敗\n錯誤提示:無網路連線\n請檢查測試機網路'
        # 發送結果到飛書機器人群組
        send_message(message_body)
    # 等待目标字符串出现
    target_string = "com.photogrid.collage.videomaker:id/uploadingVideoAni"  # 將此處替換為你要等待的字串
    poco(name=target_string).wait_for_appearance()
    start_time = time.time()  # 記錄開始時間
    print("開始第二次AI重繪")
    # 循环检查目标字符串是否存在，直到它消失或经过120秒
    sent_60s_message = False
    while poco(name=target_string).exists():
        elapsed_time = time.time() - start_time
        if elapsed_time >=60 and not sent_60s_message:
            print("已經達到60秒，發送訊息")
#             message_body = f'AI重繪第二次執行\n等待時間超過60秒'
#             send_message(message_body)
            sent_60s_message = True
        if elapsed_time >= two:
            print("已經達到120秒，中斷循環")
            stop_app(package=web)
            break
        time.sleep(1)
    if not poco(text=target_string).exists():
        operation_completed = True
    end_time = time.time()
    duration = end_time - start_time
    sleep(3.0)
    if poco(text="網絡錯誤").exists():
        # 構建訊息
        message_body = 'AI重繪第二次執行失敗\n錯誤提示:網路錯誤\n請檢查測試機網路'
        # 發送結果到飛書機器人群組
        send_message(message_body)
    if duration > two:
        print("第二次超過120秒")
        # 構建訊息
        message_body = f'【加急加急加急】\nAI重繪第二次執行\n等待時間超過120秒,請QA手動測試目前狀況'
        # 發送結果到飛書機器人群組
        send_message(message_body)
else:
    print(f"AI重繪完成！回傳時間為：{duration:.2f}秒")
