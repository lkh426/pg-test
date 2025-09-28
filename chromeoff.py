import psutil

def close_chrome():
    # 查找所有運行中的進程
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            # 檢查是否為 Chrome 進程
            if 'Google Chrome' in proc.info['name']:
                print(f'Closing process: {proc.info}')
                proc.terminate()  # 終止該進程
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

# 執行關閉 Chrome
close_chrome()