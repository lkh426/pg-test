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
    "https://www.youtube.com/shorts/DbJtnwpFeb4"
]
# 定义 Feishu Webhook URL
bot_url = 'https://open.feishu.cn/open-apis/bot/v2/hook/0a6ba36f-2dbb-41e8-92cb-ab9d93431d77'#test
# bot_url = 'https://open.feishu.cn/open-apis/bot/v2/hook/e97d3855-e320-4d43-affd-b58d300adfc7'#new

def parse_number(text):
    try:
        if '萬' in text:
            # 移除所有非数字和小数点的字符，并转换万为数字
            number = re.sub(r'[^\d.]', '', text)
            return int(float(number) * 10000)
        else:
            # 移除所有非数字字符
            number = re.sub(r'[^\d]', '', text)
            return int(number)
    except ValueError:
        print(f"无法解析文本: {text}")
        return None  # 返回 None 以处理无效情况
def get_current_time():
    """获取当前北京时间"""
    beijing_tz = timezone(timedelta(hours=8))
    current_time = datetime.now(beijing_tz).strftime('%Y-%m-%d %H:%M:%S')
    return current_time

def send_message(messages, is_test=False):
    headers = {'Content-Type': 'application/json'}
    content = []

    # 获取当前时间
    current_time = get_current_time()

    # 添加平台信息到消息内容中
    content.append([{"tag": "text", "text": f"  推广平台：YouTube"}])

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
    return "目前未展示"

# 提取 YouTube 用户名的函数
def extract_ins_name(element):
    if element.exists():
        text = element.get_name()
        print(f"提取的用户名文本: {text}")  # 调试信息
        if isinstance(text, str):
            match = re.search(r"@(\w+)", text)  # 提取@后的用户名
            if match:
                username = match.group(1)  # 提取到的用户名
                return username
            else:
                print("未找到用户名")
    return "指定的 UI 元素未找到"


# 定义一个列表来存储所有消息内容
all_message_contents = []

# 处理每个 URL
for url in insUrls:
    stop_app("com.google.android.googlequicksearchbox")
    stop_app("com.google.android.youtube")
    start_app("com.google.android.googlequicksearchbox")

    sleep(10)

    for attempt in range(3):
        url_input = poco("com.google.android.googlequicksearchbox:id/search_plate")
        if url_input.exists():
            url_input.click()
            sleep(1)
            text(url)
            keyevent("66")
            sleep(15)  # 等待页面加载
            print(f"URL {url} 输入成功")
            break
        else:
            print("URL 输入框未找到，刷新中...")
            sleep(6)
    else:
        print("多次尝试后，URL 输入框仍未找到。")

    # 尝试匹配各个计数元素
    element = poco("android.widget.FrameLayout").child("android.widget.LinearLayout")\
    .offspring("com.google.android.youtube:id/pane_fragment_container")\
    .offspring("com.google.android.youtube:id/elements_button_bar_container")\
    .child("android.view.ViewGroup").child("android.view.ViewGroup")[0]\
    .offspring(nameMatches=r"和另外\s[\d,\.]+萬\s人喜歡這部影片|和另外\s[\d,]+\s人喜歡這部影片")
        
    comment_counts = poco("android.widget.FrameLayout").child("android.widget.LinearLayout")\
    .offspring("com.google.android.youtube:id/pane_fragment_container")\
    .offspring("com.google.android.youtube:id/elements_button_bar_container")\
    .child("android.view.ViewGroup").child("android.view.ViewGroup")[2]\
    .offspring(nameMatches=r"查看\s[\d]+\s則留言")  # 正则匹配“查看 X 則留言”

    ins_name_elements = poco("android.widget.FrameLayout").child("android.widget.LinearLayout")\
    .offspring("com.google.android.youtube:id/pane_fragment_container")\
    .offspring("com.google.android.youtube:id/metapanel")\
    .child("android.view.ViewGroup")\
    .offspring(nameMatches="訂閱「@\w+」。")[0]  # 正确的使用方式


    sleep(15)
    
    # 获取元素的文本
    text = element.get_name()

    # 确保文本不为 None 并且是字符串类型
    if isinstance(text, str):
        # 调用解析函数，转换数字
        parsed_number = parse_number(text)

        if parsed_number is not None:
            print(f"转换后的数值为: {parsed_number}")
        else:
            print("无法转换文本")
    else:
        print("未能获取有效的文本或文本不是字符串")
    # 提取各个计数信息
    link_count = extract_number(element.get_name() if element.exists() else "目前未展示")
    comment_count = extract_number(comment_counts.get_name() if comment_counts.exists() else "目前未展示")
    ins_name = extract_ins_name(ins_name_elements)
    print("YouTube 用户名:", ins_name)

    message_content = f"【{ins_name}】❤️: {parsed_number} 💬: {comment_count}"
    all_message_contents.append((message_content, url))
    print("消息内容:", message_content)

send_message(all_message_contents)

stop_app("com.google.android.youtube")  # 关闭YouTube
print("YouTube已关闭")
    
