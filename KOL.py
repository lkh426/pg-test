# -*- encoding=utf8 -*-
__author__ = "jadeliu"
from airtest.core.api import *
from poco.drivers.android.uiautomation import AndroidUiautomationPoco
import json
import requests
import datetime
import re
import time
import os
import sys
import base64
import codecs
from datetime import datetime, timedelta, timezone

auto_setup(__file__)
# 修改程序的输出编码格式
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

# 初始化 Poco
poco = AndroidUiautomationPoco(use_airtest_input=True, screenshot_each_action=False)

# 要抓取的 TikTok URL 列表
TikTokUrls = [
    "https://www.tiktok.com/@mh1.120/video/7507368297403338026?_r=1&_t=ZN-8wa2M2EwDEk",
    "https://www.tiktok.com/@nevaaadaa/video/7507401898375318790?_r=1&_t=ZN-8wa2PYtjFJu",
    "https://www.tiktok.com/@itsechav/video/7507422110638214443?_r=1&_t=ZN-8wa60L0NDgE"
]

def get_data_from_element(name):
    try:
        elements = poco(name=name)
        data = [e.get_text() for e in elements] if elements else []
        return data
    except Exception as e:
        print(f"抓取数据时发生错误: {e}")
        return []

def parse_number(text):
    try:
        if 'M' in text:
            number = re.sub(r'[^\d.]', '', text)
            return int(float(number) * 1000000)
        elif 'K' in text:
            number = re.sub(r'[^\d.]', '', text)
            return int(float(number) * 1000)
        else:
            number = re.sub(r'[^\d]', '', text)
            return int(number)
    except ValueError:
        return 0
# https://open.feishu.cn/open-apis/bot/v2/hook/e97d3855-e320-4d43-affd-b58d300adfc7#new
# https://open.feishu.cn/open-apis/bot/v2/hook/0a6ba36f-2dbb-41e8-92cb-ab9d93431d77@test
def send_message(messages, combined_message):
    bot_urls = [
      'https://open.feishu.cn/open-apis/bot/v2/hook/cda387a1-8947-4821-aedd-62824a890186'#測試
        # 'https://open.feishu.cn/open-apis/bot/v2/hook/ede7a9bc-27b5-49a8-b524-f44e0294c6ea'#正式

    ]
    headers = {'Content-Type': 'application/json'}
    content = [[{"tag": "text", "text": combined_message}]]
    for message, url in messages:
        content.append([{"tag": "a", "text": message, "href": url}])
    data = {
        "msg_type": "post",
        "content": {
            "post": {
                "zh_cn": {
                    "content": content
                }
            }
        }
    }
    try:
        for bot_url in bot_urls:
            response = requests.post(bot_url, headers=headers, data=json.dumps(data))
            if response.status_code == 200:
                print(f"消息已成功发送到飞书机器人群组: {bot_url}")
            else:
                print(f"发送消息到飞书机器人群组时发生错误，状态码: {response.status_code}, URL: {bot_url}")
    except Exception as e:
        print(f"发送消息时发生错误: {e}")

def format_stats_message(name, link_count, comment_count, share_count):
    return f"【{name}】❤️:{link_count} 💬:{comment_count} 📤:{share_count}"

def open_chrome_with_url(url):
    stop_app("com.android.chrome")
    start_app("com.android.chrome")
    sleep(5)

    for i in range(3):
        url_input = poco(name="com.android.chrome:id/url_bar")
        if url_input.exists():
            url_input.click()
            sleep(8)
            print("URL 输入框已找到")
            url_input.set_text(url)
            keyevent("66")  # Enter
            sleep(8)
            break
        else:
            print("URL 输入框未找到，刷新中...")
            url_input.refresh()
            sleep(6)
    
    poco(text="繼續").click()
    sleep(10)

# 存储统计信息和链接
stats_messages = []

# 获取当前时间
# current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

# 处理每个 TikTok URL
for TikTokUrl in TikTokUrls:
    try:
        print(f"处理 URL: {TikTokUrl}")
        open_chrome_with_url(TikTokUrl)

        link_elements = poco(name='com.zhiliaoapp.musically.go:id/dnq')

        link_list = [e.get_text() for e in link_elements] if link_elements.exists() else []
        #留言
        comment_counts = get_data_from_element('com.zhiliaoapp.musically.go:id/dk7')
        #分享
        share_counts = get_data_from_element('com.zhiliaoapp.musically.go:id/ejs')

        TikTokname_element = poco(name="com.zhiliaoapp.musically.go:id/title")
        TikTokname = TikTokname_element.get_text() if TikTokname_element.exists() else "【Unknown】"

        link_count = parse_number(link_list[0]) if link_list else 0
        comment_count = parse_number(comment_counts[0]) if comment_counts else 0
        share_count = parse_number(share_counts[0]) if share_counts else 0

        if link_count > 1 or comment_count > 1 or share_count > 1:
            stats_message = format_stats_message(TikTokname, link_count, comment_count, share_count)
            stats_messages.append((stats_message, TikTokUrl))

        stop_app("com.ss.android.ugc.trill")  # 关闭抖音
        print("抖音已关闭")

    except Exception as e:
        print(f"处理 {TikTokUrl} 时发生错误: {e}")

# 生成最终消息
if stats_messages:
    combined_message = f"  推广平台：TikTok\n"  # 添加时间信息
    print(f"stats_messages ------: {stats_messages}")
    # send_message(stats_messages, combined_message)
else:
    print("没有符合条件的数据，未发送消息")
