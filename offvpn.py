from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

# 設定 Selenium 連接已開啟的 Chrome
chrome_options = Options()
chrome_options.debugger_address = "127.0.0.1:9222"  # 連接現有 Chrome 瀏覽器

# 連接已開啟的 Chrome
driver = webdriver.Chrome(options=chrome_options)

# Urban VPN 擴展 ID
extension_id = "eppiocemhmnlbhjplcgkofciiegomcon"
driver.get(f"chrome-extension://{extension_id}/popup/index.html")
time.sleep(10)  # 等待 UI 加載

# 🔹 檢查 VPN 是否開啟
try:
    timer_element = driver.find_element(By.XPATH, "//span[contains(@class, 'timer main-page__timer')]")
    vpn_time = timer_element.text.strip()
    print(f"⏳ 當前 VPN 運行時間：{vpn_time}")

    if vpn_time != "00 : 00 : 00":
        print("❌ VPN 已開啟，準備關閉...")

        # 🔹 點擊「關閉 VPN」按鈕
        try:
            vpn_button = driver.find_element(By.XPATH, "//*[@id='app']/div/div[1]/div/div[2]/div[4]/div/div")
            driver.execute_script("arguments[0].click();", vpn_button)  # 用 JS 點擊
            print("✅ VPN 已關閉！")
        except Exception as e:
            print("❌ 找不到 VPN 關閉按鈕，請確認 XPath 是否正確")
            print("錯誤訊息:", e)
    else:
        print("✅ VPN 已經關閉")
except Exception as e:
    print("❌ 無法獲取 VPN 運行時間，請確認 XPath 是否正確")
    print("錯誤訊息:", e)
    
# 🔹 在 VPN 切換後回到指定 URL
driver.get("https://ads.tiktok.com/business/creativecenter/inspiration/popular/hashtag/pc/en")
time.sleep(5)  # 等待頁面加載

# 任務完成
driver.quit()
