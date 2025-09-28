# -*- coding: utf-8 -*-
__author__ = "jade.liu"

from airtest.core.api import *
import time
auto_setup(__file__)
from poco.drivers.android.uiautomation import AndroidUiautomationPoco
import datetime
poco = AndroidUiautomationPoco(use_airtest_input=True, screenshot_each_action=False)
import requests
import json
import re
import base64
import sys   #把文本內容用utf-8印出來
import codecs

#修改程序的输出编码格式。首先，通过调用 codecs.getwriter 函数，创建一个使用 UTF-8 编码的输出流。然后，通过调用 sys.stdout.detach 方法，获取标准输出流的低层接口。最后，将新创建的输出流赋值给 sys.stdout，以替换标准输出流。这样，程序的所有输出都将使用 UTF-8 编码。
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

# 初始化 Airtest
auto_setup(__file__)

# 初始化 Poco
poco = AndroidUiautomationPoco(use_airtest_input=True, screenshot_each_action=False)

web = "com.photogrid.collage.videomaker"

# 清除資料 web包
# clear_app(package=web)
# 關閉app web包
stop_app(package=web)
# 開啟app  web包
start_app(package=web)

sleep(5.0)

# 過濾GDPR彈窗
if poco(text="開始使用").exists():
    poco(text="開始使用").click()

sleep(5.0)
# 過濾開屏
if poco(text="獨家20,000+ 拼貼畫:必備的頂級視頻編輯工具").exists():
    poco("android:id/content").offspring("android.widget.ImageView").click()

sleep(5.0)
# 看是否在首頁,是的話開始進行上色流程
if poco(text="魔法形象").exists():
    poco(text="AI修復").click()
    poco(text="立即體驗").click()

# 點擊最左上角的圖片
poco("android.widget.FrameLayout").child("android.widget.LinearLayout").offspring("com.photogrid.collage.videomaker:id/page_root").offspring("com.photogrid.collage.videomaker:id/selector_layout").offspring("com.photogrid.collage.videomaker:id/grid_container").offspring("com.photogrid.collage.videomaker:id/pic_grid").child("android.widget.RelativeLayout")[3].child("com.photogrid.collage.videomaker:id/grid_image").click()
poco(text="下一步").click()

# 等待目標字串出現
target_string = "請不要關閉應用"  # 將此處替換為你要等待的字串
poco(text=target_string).wait_for_appearance()
start_time = time.time()  # 記錄開始時間
# 如果字串出現，將繼續執行後續程式碼
print("開始進行AI修復")

# 循環檢查目標字串是否存在，直到它消失
while poco(text=target_string).exists():
    time.sleep(0.1)  # 每隔0.1秒檢查一次

# 目標字串消失後停止計時，並計算存在時間
end_time = time.time()  # 記錄結束時間
duration = end_time - start_time  # 計算存在時間

print(f"AI修復完成！回傳時間為：{duration:.2f}秒")


def send_to_feishu(title, message):
    bot_url = 'https://open.feishu.cn/open-apis/bot/v2/hook/12196b5f-51f8-4d15-b744-0bd3be07cd13'#測試群組
#     bot_url = ""#iOS
    headers = {'Content-Type': 'application/json'}
    data = {
        "msg_type": "text",
        "content": {
            "text": f"{title}\n{message}"
        }
    }
    response = requests.post(bot_url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        print("訊息已成功傳送到飛書機器人群組")
    else:
        print("傳送訊息到飛書機器人群組時發生錯誤")

# 構建訊息
message_title = 'AI修復完成'
message_body = f'回傳時間：{duration:.2f}秒'

# 發送結果到飛書機器人群組
send_to_feishu(message_title, message_body)


