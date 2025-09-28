import subprocess
import os

# 定義 Chrome 啟動命令
chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
user_data_dir = "/Users/jadeliu/selenium/ChromeProfile"
debugging_port = "9222"

# 确保用户数据目录存在
os.makedirs(user_data_dir, exist_ok=True)

# 拼接命令
command = f'"{chrome_path}" --remote-debugging-port={debugging_port} --user-data-dir="{user_data_dir}" &'

# 使用 subprocess 非阻塞运行 Chrome
subprocess.Popen(command, shell=True)
