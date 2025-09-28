import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

# 連接到現有的 Chrome 瀏覽器
def connect_to_existing_chrome():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.debugger_address = "127.0.0.1:9222"  # 使用已啟動的 Chrome
    driver = webdriver.Chrome(options=chrome_options)
    return driver


def check_and_login(driver):
    time.sleep(5)  # 等待頁面加載
    original_window = driver.current_window_handle  # 記錄原始視窗

    try:
        # 嘗試檢查是否已經登入
        try:
            # 如果已經登入，應該能找到登出按鈕
            logout_button = driver.find_element(By.XPATH, "//div[@data-testid='cc_header_logout']")
            print("✅ 已經登入，無需再次登入")
            return True  # 已經登入
        except:
            print("🚨 尚未登入，開始執行登入操作...")
        time.sleep(5)
        # 找到登入按鈕並點擊
        login_button = driver.find_element(By.XPATH, "//div[@data-testid='cc_header_login']")
        ActionChains(driver).move_to_element(login_button).click().perform()
        time.sleep(5)  # 等待登入頁面彈出
        
        time.sleep(5)
        # 找到並點擊 Google 登入按鈕
        google_login_button = driver.find_element(By.CLASS_NAME, "Button_loginBtn__ImwTi")
        print("🚨 點擊 Google 登入按鈕...")
        google_login_button.click()
        time.sleep(5)  # 等待新視窗開啟

        # 切換到新開啟的 Google 登入視窗
        all_windows = driver.window_handles
        for window in all_windows:
            if window != original_window:
                driver.switch_to.window(window)
                break

        # 定位到電子郵件輸入框並輸入帳號
        email_input = driver.find_element(By.ID, "identifierId")
        email_input.send_keys("photogrid20241024")
        email_input.send_keys(Keys.RETURN)  # 按 Enter 進行下一步
        print("✅ 帳號輸入完成，等待密碼輸入...")

        # 等待密碼輸入頁面加載
        time.sleep(10)

        
        # 定位到密碼輸入框並輸入密碼
        password_input = driver.find_element(By.XPATH, "//*[@id='password']/div[1]/div/div[1]/input")
        password_input.send_keys("xasxaswa")
        password_input.send_keys(Keys.RETURN)  # 按 Enter 完成登入
        print("✅ 密碼輸入完成，等待登入...")

        # 等待用戶手動完成額外的驗證（例如 2FA）
        input("⚡ 請手動完成 Google 驗證，完成後按 Enter 繼續...")

        # 登入完成後切回原視窗
        driver.switch_to.window(original_window)
        print("✅ 偵測到登入成功，返回原視窗！")

        # 登入成功後重新整理頁面
        driver.refresh()
        print("✅ 頁面已重新整理")
        time.sleep(10)
        return True  # 返回 True，表示登入成功
    except Exception as e:
        print(f"❌ 發生錯誤: {e}")
        return False  # 發生錯誤，登入失敗


# 主函數
def main():
    driver = connect_to_existing_chrome()
    url = "https://ads.tiktok.com/business/creativecenter/inspiration/popular/hashtag/pc/en"
    driver.get(url)
    login_success = check_and_login(driver)  # 确保已登入
    if login_success:
        print("✅ 登入成功！")
    else:
        print("❌ 登入失敗")
    driver.quit()


if __name__ == "__main__":
    main()
