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
    bot_url = 'https://open.feishu.cn/open-apis/bot/v2/hook/d732dee1-df80-4ff6-9e12-87eea731ed5d'#主要群組
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

# 清除資料
clear_app(package=web)
# 關閉app
# stop_app(package=web)
# 開啟app
start_app(package=web)


sleep(5.0)
#element=判斷的元素,identifier=元素錯誤的信息,error_message=元素不存在的信息
def click_if_exists(element, identifier, error_message):
    try:
        if element.wait(10).exists():
            element.click()
        else:
            print(error_message)
    except PocoTargetTimeout:
        print(f"超时：{identifier} 元素未能在十秒内出现")

# 操作流程
click_if_exists(poco(text="開始使用"), "開始使用", "首次開啟發生錯誤")
click_if_exists(poco(text="跳過"), "跳過", "沒有新手引導")
click_if_exists(poco(name="com.photogrid.collage.videomaker:id/premium_close_button"), "開屏關閉按钮", "沒有開屏")
click_if_exists(poco(name="com.photogrid.collage.videomaker:id/btn_close"), "新功能弹窗關閉按钮", "沒有新功能彈窗")
click_if_exists(poco(name="com.photogrid.collage.videomaker:id/btn_close"), "新功能弹窗關閉按钮", "沒有新功能彈窗")
click_if_exists(poco(text="我的"), "我的", "沒有看到首頁")
click_if_exists(poco(text="登入"), "登入", "沒有登入")
click_if_exists(poco(name="com.photogrid.collage.videomaker:id/press_view"), "google登入彈窗", "沒有彈出google登入視窗")
click_if_exists(poco(text="jade2061234@gmail.com"), "登入google帳號", "沒有彈出帳戶彈窗")
click_if_exists(poco(text="首頁"), "回到首頁", "不在APP內")
click_if_exists(poco(text="拼接"), "點擊拼接", "沒有回到首頁")
click_if_exists(poco(text="允許"), "同意存取權限", "沒有彈出權限彈窗")
click_if_exists(poco(text="允許"), "二次確認同意存取權限", "沒有彈出權限彈窗")
click_if_exists(poco(text="所有照片"), "切換相簿", "沒有彈出相簿列表")
click_if_exists(poco(text="Download"), "切換到指定的相簿", "沒有彈出相簿列表")
click_if_exists(poco(name="com.photogrid.collage.videomaker:id/selector_back"), "再次回到首頁", "不在選圖頁內")


# 看是否在首頁, 是的話開始進行智能摳圖
if poco(text="智能摳圖").wait(10).exists():
    poco(text="智能摳圖").click()
    poco("android.widget.FrameLayout").child("android.widget.LinearLayout").offspring(
        "com.photogrid.collage.videomaker:id/page_root").offspring(
        "com.photogrid.collage.videomaker:id/selector_layout").offspring(
        "com.photogrid.collage.videomaker:id/grid_container").offspring(
        "com.photogrid.collage.videomaker:id/pic_grid").child("android.widget.RelativeLayout")[0].child(
        "com.photogrid.collage.videomaker:id/grid_image").click()
else:
    print("首頁沒看到智能摳圖入口")

sleep(1.0)

#智能摳圖無網的提示內容抓取不到
if poco(text="網路不可用").exists():
    # 構建訊息
    message_body = '智能摳圖失敗\n錯誤提示:稍後再試試吧！\n請檢查測試機網路'
    # 發送結果到飛書機器人群組
    send_message(message_body)

if poco(text="無網路連線").exists():
    # 構建訊息
    message_body = '智能摳圖\n錯誤提示:無網路連線\n請檢查測試機網路'
    # 發送結果到飛書機器人群組
    send_message(message_body)

# 等待目標字串出現
target_string = "智能去背中..."  # 將此處替換為你要等待的字串
poco(text=target_string).wait_for_appearance()
start_time = time.time()  # 記錄開始時間
# 如果字串出現，將繼續執行後續程式碼
print("開始進行智能摳圖")

# 循環檢查目標字串是否存在，直到它消失或經過了120秒
sent_60s_message = False
operation_completed = False

while poco(text=target_string).exists():
    elapsed_time = time.time() - start_time

    # 如果經過的時間超過60秒但未發送訊息，則發送訊息
    if elapsed_time >= 60 and not sent_60s_message:
#         print("已經達到60秒，發送訊息")
#         message_body = f'智能摳圖\n等待時間超過60秒'
#         send_message(message_body)
        sent_60s_message = True

    # 如果經過的時間超過120秒，則中斷循環
    if elapsed_time >= 120:
        print("已經達到120秒，中斷循環")
        stop_app(package=web)
        break

    # 每隔0.1秒檢查一次
    time.sleep(1)

# 目標字串消失後停止計時，並計算存在時間
if not poco(text=target_string).exists():
    operation_completed = True

end_time = time.time()  # 記錄結束時間
duration = end_time - start_time  # 計算存在時間

sleep(3.0)

if poco(text="網絡錯誤").exists():
    # 構建訊息
    message_body = '智能摳圖失敗\n錯誤提示:網路錯誤\n請檢查測試機網路'
    # 發送結果到飛書機器人群組
    send_message(message_body)

# 檢查是否超過兩分鐘
if duration > 120:
    print("超過120秒")
    # 構建訊息
    message_body = f'智能摳圖\n等待時間超過120秒'
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
    if poco(text="智能摳圖").exists():
        poco(text="智能摳圖").click()
        poco("android.widget.FrameLayout").child("android.widget.LinearLayout").offspring(
            "com.photogrid.collage.videomaker:id/page_root").offspring(
            "com.photogrid.collage.videomaker:id/selector_layout").offspring(
            "com.photogrid.collage.videomaker:id/grid_container").offspring(
            "com.photogrid.collage.videomaker:id/pic_grid").child("android.widget.RelativeLayout")[1].child(
            "com.photogrid.collage.videomaker:id/grid_image").click()
    else:
        print("首頁沒看到智能摳圖入口")
    sleep(1.0)
    if poco(text="網路不可用").exists():
        # 構建訊息
        message_body = '智能摳圖第二次執行失敗\n錯誤提示:稍後再試試吧！\n請檢查測試機網路'
        # 發送結果到飛書機器人群組
        send_message(message_body)
    if poco(text="無網路連線").exists():
        # 構建訊息
        message_body = '智能摳圖第二次執行失敗\n錯誤提示:無網路連線\n請檢查測試機網路'
        # 發送結果到飛書機器人群組
        send_message(message_body)
    # 等待目标字符串出现
    target_string = "智能去背中..."
    poco(text=target_string).wait_for_appearance()
    start_time = time.time()
    print("開始第二次智能摳圖")
    # 循环检查目标字符串是否存在，直到它消失或经过120秒
    sent_60s_message = False
    while poco(text=target_string).exists():
        elapsed_time = time.time() - start_time
        if elapsed_time >=60 and not sent_60s_message:
            print("已經達到60秒，發送訊息")
#             message_body = f'智能摳圖第二次執行\n等待時間超過60秒'
#             send_message(message_body)
            sent_60s_message = True
        if elapsed_time >= 120:
            print("已經達到120秒，中斷循環")
            stop_app(package=web)
            break
        time.sleep(1)
    if not poco(text=target_string).exists():
        operation_completed = True
    end_time = time.time()
    duration = end_time - start_time
    sleep(1.0)
    if poco(text="網路不可用").exists():
        # 構建訊息
        message_body = '智能摳圖第二次執行失敗\n錯誤提示:網路錯誤\n請檢查測試機網路'
        # 發送結果到飛書機器人群組
        send_message(message_body)
    if duration > 120:
        print("第二次超過120秒")
        # 構建訊息
        message_body = f'【加急加急加急】\n智能摳圖第二次執行\n等待時間超過120秒,請QA手動測試目前狀況'
        # 發送結果到飛書機器人群組
        send_message(message_body)
else:
    print(f"智能摳圖完成！回傳時間為：{duration:.2f}秒")
