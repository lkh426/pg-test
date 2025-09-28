from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# 設定 Selenium 連接已開啟的 Chrome
chrome_options = Options()
chrome_options.debugger_address = "127.0.0.1:9222"  # 連接現有 Chrome 瀏覽器

# 連接已開啟的 Chrome
driver = webdriver.Chrome(options=chrome_options)

# Urban VPN 擴展 ID
extension_id = "eppiocemhmnlbhjplcgkofciiegomcon"
driver.get(f"chrome-extension://{extension_id}/popup/index.html")
time.sleep(3)  # 等待 UI 加載

# 🔹 取得當前選擇的國家
try:
    country_input = driver.find_element(By.XPATH, '//*[@id="app"]/div/div[1]/div/div[2]/div[2]/div[1]/div[1]/input')
    current_country = country_input.get_attribute("value").strip()
    print(f"🌍 當前 VPN 國家：{current_country}")
except Exception as e:
    print("❌ 無法獲取當前國家，請確認 XPath 是否正確")
    print("錯誤訊息:", e)
    driver.quit()
    exit()

# 🔹 如果當前國家不是 Algeria，則切換過去
if "Algeria" not in current_country:
    try:
        print("🔄 切換到 Algeria...")

        # 先點擊輸入框，打開國家選單
        country_input = driver.find_element(By.XPATH, '//*[@id="app"]/div/div[1]/div/div[2]/div[2]/div[1]/div[1]/input')
        country_input.click()
        time.sleep(5)  # 等待選單展開

        # 🔍 等待 Algeria 選項出現
        algeria_option = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//li[contains(@class, 'locations__item')][.//p[contains(text(), 'Algeria')]]"))
        )

        # 點擊 Algeria
        driver.execute_script("arguments[0].click();", algeria_option)  # 用 JS 點擊
        time.sleep(2)  # 等待切換
        print("✅ 成功切換到 Algeria")
    except Exception as e:
        print("❌ 無法切換到 Algeria，請確認 XPath 是否正確")
        print("錯誤訊息:", e)
        driver.quit()
        exit()
        
time.sleep(10)

# 🔹 檢查 VPN 是否開啟
try:
    timer_element = driver.find_element(By.XPATH, "//span[contains(@class, 'timer main-page__timer')]")
    vpn_time = timer_element.text.strip()
    print(f"⏳ 當前 VPN 運行時間：{vpn_time}")

    if vpn_time == "00 : 00 : 00":
        print("❌ VPN 未開啟，嘗試開啟 VPN...")

        # 🔹 點擊「開啟 VPN」按鈕
        try:
            vpn_button = driver.find_element(By.XPATH, "//*[@id='app']/div/div[1]/div/div[2]/div[4]/div/div")
            driver.execute_script("arguments[0].click();", vpn_button)  # 用 JS 點擊
            print("✅ 成功開啟 Urban VPN！")
        except Exception as e:
            print("❌ 找不到 VPN 開啟按鈕，請確認 XPath 是否正確")
            print("錯誤訊息:", e)
    else:
        print("✅ VPN 已經開啟")
except Exception as e:
    print("❌ 無法獲取 VPN 運行時間，請確認 XPath 是否正確")
    print("錯誤訊息:", e)

# 🔹 在 VPN 切換後回到指定 URL
driver.get("https://ads.tiktok.com/business/creativecenter/inspiration/popular/hashtag/pc/en")
time.sleep(5)  # 等待頁面加載

# 關閉瀏覽器
driver.quit()

