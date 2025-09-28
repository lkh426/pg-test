import requests
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from datetime import datetime

# 連接到現有的 Chrome 瀏覽器
def connect_to_existing_chrome():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.debugger_address = "127.0.0.1:9222"  # 連接已開啟的 Chrome 瀏覽器
    driver = webdriver.Chrome(options=chrome_options)
    return driver

# 切換到 "Table" 分類
def switch_to_table_tab(driver):
    try:
        table_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Table')]")
        ActionChains(driver).move_to_element(table_button).click().perform()
        time.sleep(20)  # 等待頁面刷新
        print("✅ 成功切換到 Table 分類")
    except Exception as e:
        print("❌ 切換 Table 分類失敗，請確認 XPath 是否正確")
        print("錯誤訊息:", e)

# 爬取 trends24 表格數據
def scrape_tiktok_hot_hashtags(driver, url):
    driver.get(url)
    time.sleep(20)  # 等待頁面加載

    switch_to_table_tab(driver)  # 確保切換到 Table 分類

    hashtags = []

    for index in range(1, 21):  # 抓取前 20 名
        try:
            rank_xpath = f"(//table[contains(@class, 'table')])[1]/tbody/tr[{index}]/td[1]"
            topic_xpath = f"(//table[contains(@class, 'table')])[1]/tbody/tr[{index}]/td[2]/a"

            rank = driver.find_element(By.XPATH, rank_xpath).text.strip()
            topic_element = driver.find_element(By.XPATH, topic_xpath)
            topic = topic_element.text.strip()
            topic_link = topic_element.get_attribute('href')  # 直接獲取 X/Twitter 話題鏈接

            hashtags.append({
                "rank": rank,
                "topic": topic,
                "link": topic_link
            })
        except Exception as e:
            print(f"❌ 抓取 Rank {index} 失敗，錯誤: {e}")

    return hashtags

# 發送飛書消息
def send_post_to_feishu(hashtags):
    # feishu_webhook_url = "https://open.feishu.cn/open-apis/bot/v2/hook/760cc0ee-76f1-402a-88df-72def7006e84"#朱比特机器人账号
    feishu_webhook_url = "https://open.feishu.cn/open-apis/bot/v2/hook/a84d7b74-3c2f-4548-bd6b-b7557d436bb2"#乐我机器人特账号
#     feishu_webhook_url = "https://open.feishu.cn/open-apis/bot/v2/hook/0a6ba36f-2dbb-41e8-92cb-ab9d93431d77"
#     feishu_webhook_url = "https://open.feishu.cn/open-apis/bot/v2/hook/407dee39-3ae0-4a4b-a39f-4709a0b61ae1"
    title = f"【USA】【{datetime.now().strftime('%Y-%m-%d')} X 熱點話題】\n\n"
    content = []

    for tag in hashtags:
        content.append([
            {"tag": "text", "text": f'{tag["rank"]}. '},
            {"tag": "a", "text": f'{tag["topic"]}', "href": tag["link"]}  # 超鏈接跳轉 X/Twitter 話題
        ])

    payload = {
        "msg_type": "post",
        "content": {
            "post": {
                "zh_cn": {
                    "title": title.strip(),
                    "content": content
                }
            }
        }
    }

    response = requests.post(feishu_webhook_url, json=payload)
    if response.status_code == 200:
        print("✅ 消息已成功發送到飛書")
    else:
        print(f"❌ 發送消息失敗: {response.status_code}, 返回信息: {response.text}")

# 主函數，增加自動重試機制
def main(retry_count=3):
    attempt = 0

    while attempt < retry_count:
        print(f"📌 第 {attempt + 1} 次嘗試抓取數據...")
        driver = connect_to_existing_chrome()

        url = "https://trends24.in/united-states/"
        hashtags = scrape_tiktok_hot_hashtags(driver, url)

        if hashtags and len(hashtags) >= 10:  # 確保至少有 10 筆數據
            send_post_to_feishu(hashtags)
            print("✅ 成功獲取數據，並發送到飛書")
            driver.quit()
            return  # 成功後結束函數
        
        print("⚠️ 爬取數據不完整，準備重新執行...")
        driver.quit()
        attempt += 1
        time.sleep(10)  # 避免過於頻繁請求

    print("❌ 多次重試仍未獲取完整數據，請手動檢查問題！")

if __name__ == "__main__":
    main()
