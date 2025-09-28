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

poco = AndroidUiautomationPoco(use_airtest_input=True, screenshot_each_action=False)

insUrls = [
   # "https://www.instagram.com/reel/DE2hEEqvKAC/?utm_source=ig_web_copy_link",
    "https://www.instagram.com/p/DObD_EHETca/?utm_source=ig_web_copy_link"
]


# 定义 Feishu Webhook URL
# bot_url = 'https://open.feishu.cn/open-apis/bot/v2/hook/0a6ba36f-2dbb-41e8-92cb-ab9d93431d77'#test
bot_url = 'https://open.feishu.cn/open-apis/bot/v2/hook/e97d3855-e320-4d43-affd-b58d300adfc7'#new

def get_current_time():
    beijing_tz = timezone(timedelta(hours=8))
    current_time = datetime.now(beijing_tz).strftime('%Y-%m-%d %H:%M:%S')
    return current_time

def send_message(messages, is_test=False):
    headers = {'Content-Type': 'application/json'}
    content = []

    # 获取当前时间
    current_time = get_current_time()

    # 添加平台信息到消息内容中
    content.append([{"tag": "text", "text": f"  推广平台：ins"}])

    # 添加每条消息到内容中
    for message, url in messages:
        # 将每个消息格式化为段落
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
        response = requests.post(bot_url, headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            msg_type = "测试消息" if is_test else "消息"
            print(f"{msg_type}已成功发送到飞书机器人群组")
        else:
            print(f"发送消息到飞书机器人群组时发生错误，状态码: {response.status_code}")
            print("响应内容:", response.text)
    except Exception as e:
        print(f"发送消息时发生错误: {e}")


# 提取数字的通用函数
def extract_number(text):
    """从文本中提取数字"""
    if isinstance(text, str):
        # 使用正则表达式提取所有数字
        matches = re.findall(r'\d+', text)
        # 处理逗号分隔的数字
        if matches:
            return ''.join(matches)  # 将所有匹配的数字连接起来
    return "無"

# 提取 Instagram 用户名的函数
def extract_ins_name(element):
    if element.exists():
        text = element.get_name()
        print(f"提取的用户名文本: {text}")  # 调试信息
        if isinstance(text, str):
            name = text.split("的大頭貼照")[0]
            return name
    return "指定的 UI 元素未找到"

# 定义一个列表来存储所有消息内容
all_message_contents = []

# 处理每个 URL
for url in insUrls:
    stop_app("com.google.android.googlequicksearchbox")
    start_app("com.google.android.googlequicksearchbox")
    sleep(10)

    for attempt in range(3):
        url_input = poco("com.google.android.googlequicksearchbox:id/search_plate")
        if url_input.exists():
            url_input.click()
            sleep(1)
            text(url)
            keyevent("66")
            sleep(12)  # 等待页面加载

            if poco(text="開啟 Instagram").exists():
                poco(text="開啟 Instagram").click()
            else:
                print("没有找到 '開啟 Instagram' 的字串")

            if poco(text="開啟 Instagram Lite").exists():
                poco(text="開啟 Instagram Lite").click()
            else:
                print("没有找到 '開啟 Instagram Lite' 的字串")

            print(f"URL {url} 输入成功")
            sleep(12)  # 等待Instagram页面加载
            break
        else:
            print("URL 输入框未找到，刷新中...")
            sleep(6)
    else:
        print("多次尝试后，URL 输入框仍未找到。")

    # 尝试匹配各个计数元素
    
    link_elements = poco("android.widget.FrameLayout").child("android.widget.LinearLayout").offspring("androidx.recyclerview.widget.RecyclerView").child("android.widget.FrameLayout").child("android.view.ViewGroup").child("android.view.ViewGroup")[0].child("android.view.ViewGroup")[0].offspring(nameMatches=r"\d+個讚。查看說讚的內容")

    comment_counts = poco("android.widget.FrameLayout").child("android.widget.LinearLayout").offspring("androidx.recyclerview.widget.RecyclerView").child("android.widget.FrameLayout").child("android.view.ViewGroup").child("android.view.ViewGroup")[0].child("android.view.ViewGroup")[0].offspring(nameMatches=r"\d+則留言。查看留言")


    share_counts =  poco("android.widget.FrameLayout").child("android.widget.LinearLayout").offspring("androidx.recyclerview.widget.RecyclerView").child("android.widget.FrameLayout").child("android.view.ViewGroup").child("android.view.ViewGroup")[0].child("android.view.ViewGroup")[0].offspring(nameMatches=r"轉貼次數為\d+次")
       

    ins_name_elements = poco("android.widget.FrameLayout").child("android.widget.LinearLayout").offspring("androidx.recyclerview.widget.RecyclerView").child("android.widget.FrameLayout").child("android.view.ViewGroup").offspring("com.instagram.android:id/reels_clips_media_info_component")[0].child("android.view.ViewGroup").offspring(nameMatches=r".*的大頭貼照")

     # 确保正确点击查看播放次数
    def click_view_likes_or_comments():
        # 尝试点击“查看说赞的内容”
        like_button = poco("android.widget.FrameLayout").child("android.widget.LinearLayout").offspring("androidx.recyclerview.widget.RecyclerView").child("android.widget.FrameLayout").child("android.view.ViewGroup").child("android.view.ViewGroup")[0].child("android.view.ViewGroup")[0].offspring(nameMatches=r"\d+個讚。查看說讚的內容")

        if like_button.exists():
            like_button.click()
            print("点击了 '查看说赞的内容'")
        else:
            # 如果没有找到“查看说赞的内容”，尝试点击“查看说赞的用户”
            comment_button = poco("android.widget.FrameLayout").child("android.widget.LinearLayout").offspring("androidx.recyclerview.widget.RecyclerView").child("android.widget.FrameLayout").child("android.view.ViewGroup").child("android.view.ViewGroup")[1].child("android.view.ViewGroup")[0].offspring(nameMatches=r"查看說讚的用戶")
   
            if comment_button.exists():
                comment_button.click()
                print("点击了 '查看说赞的用户'")
            else:
                print("既没有找到 '查看说赞的内容' 也没有找到 '查看说赞的用户'")

        # 执行点击操作
    click_view_likes_or_comments()
    
    sleep(15)
    
    play_countsn = poco(name="com.instagram.android:id/play_count_text")
    play_counts = play_countsn.get_text() if play_countsn.exists() else "無"

    # 提取各个计数信息
    link_count = extract_number(link_elements.get_name() if link_elements.exists() else "無")
    comment_count = extract_number(comment_counts.get_name() if comment_counts.exists() else "無")
    share_count = extract_number(share_counts.get_name() if share_counts.exists() else "無")
    play_count = extract_number(play_counts)
    print(play_count)
    ins_name = extract_ins_name(ins_name_elements)
    print("ins 用户名:", ins_name)
# 📤:{share_count}
    message_content = f"【{ins_name}】▶️:{play_count} ❤️:{link_count} 💬:{comment_count}"
    all_message_contents.append((message_content, url))
    print("消息内容:", message_content)

send_message(all_message_contents)

stop_app("com.instagram.android")  # 关闭ig
print("ig已关闭")
    
