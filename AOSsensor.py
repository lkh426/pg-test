# -*- encoding=utf8 -*-
__author__ = "jadeliu"
import os
import requests
import codecs
import sys
from airtest.core.api import *
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from datetime import datetime

auto_setup(__file__)
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

# 设置飞书 webhook URL 和应用相关信息
# feishu_webhook_url = "https://open.feishu.cn/open-apis/bot/v2/hook/9ad7c8be-abdb-494a-898a-b1e3650a4633"#朱比特機器人账号位置
feishu_webhook_url = "https://open.feishu.cn/open-apis/bot/v2/hook/f631dcbc-ac7e-4a71-b43c-65f4bba08192"#乐我機器人账号位置
# feishu_webhook_url = "https://open.feishu.cn/open-apis/bot/v2/hook/cda387a1-8947-4821-aedd-62824a890186"#乐我测试機器人位置
# feishu_webhook_url = "https://open.feishu.cn/open-apis/bot/v2/hook/0a6ba36f-2dbb-41e8-92cb-ab9d93431d77"#測試
app_id = "cli_a79de5bd2d2cd00d"
app_secret = "8hLFlbGYdyfQQLs2XSHtXbR1SCwYbCzv"
image_path = "/Users/Shared/sensor/screenshot.png"

# 截图并保存到本地
def capture_screenshot(driver, image_path):
    driver.save_screenshot(image_path)
    print(f"截图已保存到: {image_path}")

# 上传图片到飞书
def upload_image_to_feishu(image_path, tenant_access_token):
    upload_url = "https://open.feishu.cn/open-apis/im/v1/images"
    headers = {"Authorization": f"Bearer {tenant_access_token}"}

    with open(image_path, 'rb') as image_file:
        files = {
            'image_type': (None, 'message'),
            'image': ('screenshot.png', image_file, 'image/png')
        }
        response = requests.post(upload_url, headers=headers, files=files)

    if response.status_code == 200:
        image_key = response.json().get("data", {}).get("image_key")
        print(f"图片上传成功，image_key: {image_key}")
        return image_key
    else:
        print(f"图片上传失败，状态码: {response.status_code}，返回信息: {response.text}")
        return None

# 通过 webhook 发送日期消息到飞书
def send_date_to_feishu_via_webhook():
    today_date = datetime.now().strftime("%Y-%m-%d")  # 获取今天的日期
    payload = {
        "msg_type": "text",
        "content": {
            "text": f"【{today_date} 安卓商业报表】"
        }
    }
    response = requests.post(feishu_webhook_url, json=payload)
    if response.status_code == 200:
        print("日期已成功发送到飞书")
    else:
        print(f"发送日期到飞书失败: {response.status_code}，返回信息: {response.text}")

# 通过 webhook 发送图片消息到飞书
def send_image_to_feishu_via_webhook(image_key):
    if image_key:
        payload = {
            "msg_type": "image",
            "content": {"image_key": image_key}
        }
        response = requests.post(feishu_webhook_url, json=payload)
        if response.status_code == 200:
            print("图片已成功发送到飞书")
        else:
            print(f"发送图片到飞书失败: {response.status_code}，返回信息: {response.text}")
    else:
        print("无效的 image_key，无法发送")

# 获取 tenant_access_token
def get_tenant_access_token(app_id, app_secret):
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    payload = {
        "app_id": app_id,
        "app_secret": app_secret
    }
    response = requests.post(url, json=payload)

    if response.status_code == 200:
        tenant_access_token = response.json().get("tenant_access_token")
        print(f"tenant_access_token 获取成功: {tenant_access_token}")
        return tenant_access_token
    else:
        print(f"获取 tenant_access_token 失败: {response.text}")
        return None

# 主函数
def main():
    # 设置 Chrome 驱动的路径
    service = Service('/Users/jadeliu/Downloads/chromedriver-mac-x64/chromedriver')
    driver = webdriver.Chrome(service=service)  # 使用 service 参数来初始化
    driver.implicitly_wait(20)  # 全局等待
    # driver.get("https://sensor.photogrid.app:8107/dashboard/?project=PG&product=sbp_family&id=198&dash_type=lego")#網址
    driver.get("http://livemesensor.ksmobile.com:8107/dashboard/?project=PG&product=sensors_analysis&id=2018&dash_type=lego")#網址
    driver.maximize_window()

    # 登录
    # log_button = driver.find_element(By.XPATH, '//*[@id="rc-tabs-0-tab-project"]/div/span')
    # log_button.click()

    account_input = driver.find_element(By.XPATH, '//*[@id="rc-tabs-0-panel-project"]/div/form/div[2]/div/div/span/span/input')
    # account_input.send_keys("pg-test@ijoyful.com")
    account_input.send_keys("data_qa@liveme.com")

    password_input = driver.find_element(By.XPATH, '//*[@id="rc-tabs-0-panel-project"]/div/form/div[3]/div/div/span/span[1]/input')
    # password_input.send_keys("PGtest123.")
    password_input.send_keys("PGPGqaqa@111")

    login_button = driver.find_element(By.XPATH, '//*[@id="rc-tabs-0-panel-project"]/div/form/div[4]/div/div/span/button')
    login_button.click()

    time.sleep(50)  # 等待登录完成

    # 截图
    capture_screenshot(driver, image_path)

    # 获取飞书 tenant_access_token
    tenant_access_token = get_tenant_access_token(app_id, app_secret)

    if tenant_access_token:
        # 首先发送日期消息
        send_date_to_feishu_via_webhook()

        # 上传图片到飞书并通过 webhook 发送图片
        image_key = upload_image_to_feishu(image_path, tenant_access_token)
        if image_key:
            send_image_to_feishu_via_webhook(image_key)

    driver.quit()  # 关闭所有关联窗口

if __name__ == "__main__":
    main()


