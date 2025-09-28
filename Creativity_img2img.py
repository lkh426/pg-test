import collections
if not hasattr(collections, 'MutableMapping'):
    import collections.abc
    collections.MutableMapping = collections.abc.MutableMapping

from airtest.core.api import *
from poco.drivers.android.uiautomation import AndroidUiautomationPoco
from poco.drivers.unity3d import UnityPoco
from poco.exceptions import PocoNoSuchNodeException, PocoTargetTimeout
import time
import json
import requests
import os
import sys
import datetime
import re
import base64
import codecs

# 修改程序的輸出編碼格式為 UTF-8
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

# 初始化Airtest
auto_setup(__file__)

# 初始化Poco
poco = AndroidUiautomationPoco(use_airtest_input=True, screenshot_each_action=False)

web = "com.photogrid.collage.videomaker"
xy = poco.get_screen_size()  # 把手機size存到xy
x = xy[0]  # X
y = xy[1]  # Y

# 定義發送訊息函數
def send_message(message):
    # bot_url = 'https://open.feishu.cn/open-apis/bot/v2/hook/d732dee1-df80-4ff6-9e12-87eea731ed5d'#朱比特账号机器人主要群組
    bot_url = 'https://open.feishu.cn/open-apis/bot/v2/hook/215772c2-3833-4996-9407-9ba67b8a1be4'#乐我机器人账号后
    # bot_url = 'https://open.feishu.cn/open-apis/bot/v2/hook/0a6ba36f-2dbb-41e8-92cb-ab9d93431d77' # 測試機器人
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

# 清除資料並關閉app
# clear_app(package=web)
stop_app(package=web)

# 開啟app
start_app(package=web)

sleep(5.0)

one = 120
two = 120
# 檢查是否在首頁，若是則進行超清畫質設置
if poco(text="編輯").exists():
    poco(text="編輯").click()
    poco("android.widget.FrameLayout").child("android.widget.LinearLayout").offspring("com.photogrid.collage.videomaker:id/page_root").offspring("com.photogrid.collage.videomaker:id/selector_layout").offspring("com.photogrid.collage.videomaker:id/grid_container").offspring("com.photogrid.collage.videomaker:id/pic_grid").child("android.widget.RelativeLayout")[0].child("com.photogrid.collage.videomaker:id/grid_image").click()
    swipe((0.9*x, 0.9*y), (0.1*x, 0.9*y))
    poco(text="AI特效").click()

    # 遍歷點擊指定的AI特效
    for i in range(20):
        if poco(text="Bratz Doll").exists():
            poco(text="Bratz Doll").click()
            break
        else:
            swipe((0.9*x, 0.9*y), (0.1*x, 0.9*y))
else:
    print("首頁沒看到編輯")
sleep(3.0)
# 處理網絡錯誤
if poco(text="無網路連線").exists():
    send_message('AI風格化失敗(img2img)\生成失敗\n請QA手動測試目前狀況')

if poco(text="網絡錯誤，請再試一次。").exists():
    send_message('AI風格化失敗(img2img)\n錯誤提示:網路錯誤\n請檢查測試機網路')

# 等待目標字串出現並計時
target_string = "上傳雲端處理特效中，請耐心等待"
poco(text=target_string).wait_for_appearance()
start_time = time.time()

print("開始進行AI風格化(img2img)")
sleep(3.0)
# 檢查目標字串存在時間，超過指定時間則發送通知
sent_60s_message = False
while poco(text=target_string).exists():
    elapsed_time = time.time() - start_time

    if elapsed_time >= 60 and not sent_60s_message:
#         send_message('AI風格化(img2img)\n等待時間超過120秒')
        sent_60s_message = True

    if elapsed_time >= one:
#         send_message('AI風格化(img2img)\n等待時間超過120秒,請手動測試目前狀況')
        stop_app(package=web)
        break

    time.sleep(1)

if not poco(text=target_string).exists():
    operation_completed = True

end_time = time.time()
duration = end_time - start_time

sleep(3.0)

if poco(text="網絡錯誤，請再試一次。").exists():
    send_message('AI風格化(img2img)生成失敗\n請QA手動測試目前狀況')
    print("開始第二次執行")
    auto_setup(__file__)
    poco = AndroidUiautomationPoco(use_airtest_input=True, screenshot_each_action=False)
    stop_app(package=web)
    start_app(package=web)
    sleep(5.0)

    if poco(text="編輯").exists():
        poco(text="編輯").click()
        poco("android.widget.FrameLayout").child("android.widget.LinearLayout").offspring("com.photogrid.collage.videomaker:id/page_root").offspring("com.photogrid.collage.videomaker:id/selector_layout").offspring("com.photogrid.collage.videomaker:id/grid_container").offspring("com.photogrid.collage.videomaker:id/pic_grid").child("android.widget.RelativeLayout")[0].child("com.photogrid.collage.videomaker:id/grid_image").click()
        swipe((0.9*x, 0.9*y), (0.1*x, 0.9*y))
        poco(text="AI特效").click()

        for i in range(20):
            if poco(text="Bratz Doll").exists():
                poco(text="Bratz Doll").click()
                break
            else:
                swipe((0.9*x, 0.9*y), (0.1*x, 0.9*y))
        else:
            print("首頁沒看到編輯")

        sleep(1.0)

        if poco(text="網絡錯誤").exists():
            send_message('AI風格化(img2img)第二次執行失敗\n錯誤提示:稍後再試試吧！\n請檢查測試機網路')

        if poco(text="網絡錯誤，請再試一次。").exists():
            send_message('AI風格化(img2img)第二次執行失敗\n錯誤提示:無網路連線\n請檢查測試機網路')

        target_string = "上傳雲端處理特效中，請耐心等待"
        poco(text=target_string).wait_for_appearance()
        start_time = time.time()
        sleep(3.0)
        print("開始第二次AI風格化(img2img)")

        sent_60s_message = False
        while poco(text=target_string).exists():
            elapsed_time = time.time() - start_time
            if elapsed_time >= 60 and not sent_60s_message:
#                 send_message('AI風格化第二次執行\n等待時間超過120秒')
                sent_60s_message = True
            if elapsed_time >= two:
                send_message('【加急加急加急】\nAI風格化(img2img)第二次執行\n等待時間超過120秒,請QA手動測試目前狀況')
                stop_app(package=web)
                break
            time.sleep(1)

        if not poco(text=target_string).exists():
            operation_completed = True

        end_time = time.time()
        duration = end_time - start_time

        sleep(3.0)

        if poco(text="網絡錯誤，請再試一次。").exists():
            send_message('【加急加急加急】\nAI風格化(img2img)第二次執行\n生成失敗,請QA手動測試目前狀況')

else:
    print(f"AI風格化(img2img)完成！回傳時間為：{duration:.2f}秒")
    
    
if duration > one:
    send_message('AI風格化(img2img)\n等待時間超過120秒')

    print("開始第二次執行")
    auto_setup(__file__)
    poco = AndroidUiautomationPoco(use_airtest_input=True, screenshot_each_action=False)
    stop_app(package=web)
    start_app(package=web)
    sleep(5.0)

    if poco(text="編輯").exists():
        poco(text="編輯").click()
        poco("android.widget.FrameLayout").child("android.widget.LinearLayout").offspring("com.photogrid.collage.videomaker:id/page_root").offspring("com.photogrid.collage.videomaker:id/selector_layout").offspring("com.photogrid.collage.videomaker:id/grid_container").offspring("com.photogrid.collage.videomaker:id/pic_grid").child("android.widget.RelativeLayout")[0].child("com.photogrid.collage.videomaker:id/grid_image").click()
        swipe((0.9*x, 0.9*y), (0.1*x, 0.9*y))
        poco(text="AI特效").click()

        for i in range(20):
            if poco(text="Bratz Doll").exists():
                poco(text="Bratz Doll").click()
                break
            else:
                swipe((0.9*x, 0.9*y), (0.1*x, 0.9*y))
        else:
            print("首頁沒看到編輯")

        sleep(1.0)

        if poco(text="網絡錯誤").exists():
            send_message('AI風格化(img2img)第二次執行失敗\n錯誤提示:稍後再試試吧！\n請檢查測試機網路')

        if poco(text="網絡錯誤，請再試一次。").exists():
            send_message('AI風格化(img2img)第二次執行失敗\n錯誤提示:無網路連線\n請檢查測試機網路')

        target_string = "上傳雲端處理特效中，請耐心等待"
        poco(text=target_string).wait_for_appearance()
        start_time = time.time()

        print("開始第二次AI風格化(img2img)")

        sent_60s_message = False
        while poco(text=target_string).exists():
            elapsed_time = time.time() - start_time
            if elapsed_time >= 60 and not sent_60s_message:
#                 send_message('AI風格化第二次執行\n等待時間超過120秒')
                sent_60s_message = True
            if elapsed_time >= two:
                send_message('【加急加急加急】\nAI風格化(img2img)第二次執行\n等待時間超過120秒,請QA手動測試目前狀況')
                stop_app(package=web)
                break
            time.sleep(1)

        if not poco(text=target_string).exists():
            operation_completed = True

        end_time = time.time()
        duration = end_time - start_time

        sleep(3.0)

        if poco(text="網絡錯誤，請再試一次。").exists():
            send_message('【加急加急加急】\nAI風格化(img2img)第二次執行\n生成失敗,請QA手動測試目前狀況')

else:
    print(f"AI風格化(img2img)完成！回傳時間為：{duration:.2f}秒")

print("腳本執行完成")
