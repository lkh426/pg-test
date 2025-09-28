import requests
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from datetime import datetime
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 連接到現有的 Chrome 瀏覽器
def connect_to_existing_chrome():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.debugger_address = "127.0.0.1:9222"  # 使用已啟動的 Chrome
    driver = webdriver.Chrome(options=chrome_options)
    return driver

# 爬取 TikTok 熱門標籤數據
def scrape_tiktok_hot_hashtags(driver, url):
    driver.get(url)
    time.sleep(20)

    try:
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/main/div[3]/div/div[1]/div[2]/a"))
        )
    except Exception as e:
        print(f"❌ 等待頁面加載時出錯: {e}")

    try:
        load_more_button = driver.find_element(By.XPATH, '//*[@id="ccContentContainer"]/div[3]/div/div[2]/div/div[1]/div')
        for i in range(6):
            print(f"📌 點擊加載更多按鈕（第 {i+1} 次）")
            load_more_button.click()
            time.sleep(3)
    except Exception as e:
        print("⚠️ 未找到加載更多按鈕，可能無需點擊")

    hashtags = []
    for index in range(2, 22):
        try:
            rank = driver.find_element(By.XPATH, f"/html/body/div[1]/div/main/div[3]/div/div[1]/div[{index}]/a/div[1]/span").text
            hashtag = driver.find_element(By.XPATH, f"/html/body/div[1]/div/main/div[3]/div/div[1]/div[{index}]/a/div[2]/div[1]").text
            posts = driver.find_element(By.XPATH, f"/html/body/div[1]/div/main/div[3]/div/div[1]/div[{index}]/a/div[3]").text.replace("\n", " ").strip()
            posts = posts.replace(" Posts", "")
            action_link = driver.find_element(By.XPATH, f"/html/body/div[1]/div/main/div[3]/div/div[1]/div[{index}]/a").get_attribute('href')
            hashtags.append({"rank": rank, "hashtag": hashtag, "posts": posts, "action_link": action_link})
        except Exception as e:
            print(f"❌ 抓取 Rank {index} 失敗，錯誤: {e}")
    
    return hashtags

# 發送飛書消息
def send_post_to_feishu(hashtags):
    # feishu_webhook_url = "https://open.feishu.cn/open-apis/bot/v2/hook/cda387a1-8947-4821-aedd-62824a890186"#test机器人账号
    feishu_webhook_url = "https://open.feishu.cn/open-apis/bot/v2/hook/a84d7b74-3c2f-4548-bd6b-b7557d436bb2"#乐我机器人特账号
#     feishu_webhook_url = "https://open.feishu.cn/open-apis/bot/v2/hook/0a6ba36f-2dbb-41e8-92cb-ab9d93431d77"
#     feishu_webhook_url = "https://open.feishu.cn/open-apis/bot/v2/hook/407dee39-3ae0-4a4b-a39f-4709a0b61ae1"
    title = f"【USA】【{datetime.now().strftime('%Y-%m-%d')} TikTok 熱點標籤】\n\n"
    
    content = []
    for tag in hashtags:
        content.append([
            {"tag": "text", "text": f'{tag["rank"]}. '},
            {"tag": "a", "text": f'{tag["hashtag"]} : ', "href": tag["action_link"]},
            {"tag": "text", "text": f'{tag["posts"]}'}
        ])

    payload = {
        "msg_type": "post",
        "content": {"post": {"zh_cn": {"title": title.strip(), "content": content}}}
    }

    response = requests.post(feishu_webhook_url, json=payload)
    if response.status_code == 200:
        print("✅ 消息已成功發送到飛書")
    else:
        print(f"❌ 發送消息失敗: {response.status_code}, 返回信息: {response.text}")

# 主函數
def main():
    driver = connect_to_existing_chrome()
    url = "https://ads.tiktok.com/business/creativecenter/inspiration/popular/hashtag/pc/en"
    hashtags = scrape_tiktok_hot_hashtags(driver, url)
    send_post_to_feishu(hashtags)
    driver.quit()

if __name__ == "__main__":
    main()
