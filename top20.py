import requests
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import datetime
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
# 連接到現有的 Chrome 瀏覽器
def connect_to_existing_chrome():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.debugger_address = "127.0.0.1:9222"  # 使用您啟動的遠端除錯端口

    # 連接到現有的 Chrome 瀏覽器
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
    for index in range(2, 22):  # 只抓取前 30 個
        try:
            rank = driver.find_element(By.XPATH, f"/html/body/div[1]/div/main/div[3]/div/div[1]/div[{index}]/a/div[1]/span").text
            hashtag = driver.find_element(By.XPATH, f"/html/body/div[1]/div/main/div[3]/div/div[1]/div[{index}]/a/div[2]/div[1]").text
            posts = driver.find_element(By.XPATH, f"/html/body/div[1]/div/main/div[3]/div/div[1]/div[{index}]/a/div[3]").text.replace("\n", " ").strip()
            posts = posts.replace(" Posts", "")  # 去掉 "Posts"
            action_link = driver.find_element(By.XPATH, f"/html/body/div[1]/div/main/div[3]/div/div[1]/div[{index}]/a").get_attribute('href')

            # 存入列表
            hashtags.append({
                "rank": rank,
                "hashtag": hashtag,
                "posts": posts,
                "action_link": action_link
            })
        except Exception as e:
            print(f"❌ 抓取 Rank {index} 失敗，錯誤: {e}")
    
    return hashtags

# 發送飛書消息
def send_post_to_feishu(hashtags):
    # feishu_webhook_url = "https://open.feishu.cn/open-apis/bot/v2/hook/760cc0ee-76f1-402a-88df-72def7006e84"#朱比特机器人账号
    feishu_webhook_url = "https://open.feishu.cn/open-apis/bot/v2/hook/a84d7b74-3c2f-4548-bd6b-b7557d436bb2"#乐我机器人特账号
    # feishu_webhook_url = "https://open.feishu.cn/open-apis/bot/v2/hook/407dee39-3ae0-4a4b-a39f-4709a0b61ae1"#test机器人特账号
#     feishu_webhook_url = "https://open.feishu.cn/open-apis/bot/v2/hook/0a6ba36f-2dbb-41e8-92cb-ab9d93431d77"
#     feishu_webhook_url = "https://open.feishu.cn/open-apis/bot/v2/hook/407dee39-3ae0-4a4b-a39f-4709a0b61ae1"
    # 構造標題
    title = f"【All】【{datetime.now().strftime('%Y-%m-%d')} TikTok 熱點標籤】\n\n"
    
    
#     構造富文本內容
    content = [
#         [{"tag": "text", "text": title}]  # 确保标题是第一部分
    ]

    for tag in hashtags:
        content.append([
            {"tag": "text", "text": f'{tag["rank"]}. '},
            {"tag": "a", "text": f'{tag["hashtag"]} : ', "href": tag["action_link"]},  # 讓 HASHTAG 變成超鏈接
            {"tag": "text", "text": f'{tag["posts"]}'}  # 只保留數字，去掉 "Posts"
        ])

    payload = {
        "msg_type": "post",
        "content": {
            "post": {
                "zh_cn": {
                    "title": title.strip(),  # 这里可以加个标题，飞书会单独显示
                    "content": content  # 確保只有一個標題
                }
            }
        }
    }

    response = requests.post(feishu_webhook_url, json=payload)
    if response.status_code == 200:
        print("✅ 消息已成功發送到飛書")
    else:
        print(f"❌ 發送消息失敗: {response.status_code}, 返回信息: {response.text}")
    
# 主函數
def main():
    # 連接到現有的 Chrome 瀏覽器
    driver = connect_to_existing_chrome()

    url = "https://ads.tiktok.com/business/creativecenter/inspiration/popular/hashtag/pc/en"
    hashtags = scrape_tiktok_hot_hashtags(driver, url)
    
    send_post_to_feishu(hashtags)
    
    driver.quit()

if __name__ == "__main__":
    main()
