# -*- coding: utf-8 -*-
__author__ = "jade.liu"

from airtest.core.api import *
import time
auto_setup(__file__)
from poco.drivers.android.uiautomation import AndroidUiautomationPoco
import datetime
poco = AndroidUiautomationPoco(use_airtest_input=True, screenshot_each_action=False)
import requests
import json
import re
import base64
import sys   #把文本內容用utf-8印出來
import codecs

#修改程序的输出编码格式。首先，通过调用 codecs.getwriter 函数，创建一个使用 UTF-8 编码的输出流。然后，通过调用 sys.stdout.detach 方法，获取标准输出流的低层接口。最后，将新创建的输出流赋值给 sys.stdout，以替换标准输出流。这样，程序的所有输出都将使用 UTF-8 编码。
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

xy = poco.get_screen_size()#把手機size存到xy
x = xy[0]#X
y = xy[1]#Y

start_app("com.android.chrome")#開啟瀏覽器
sleep(6.0)

for i in range(3):
    home_btn =  poco(name="com.android.chrome:id/home_button")
    if home_btn and home_btn.exists():
        home_btn.click()
        sleep(6.0)
        break
    else:
        home_btn.refresh()
        sleep(6.0)
#已經登入帳號的firebase
poco(name="com.android.chrome:id/search_box_text").set_text("https://console.firebase.google.com/u/0/project/photogrid-42441/crashlytics/app/ios:com.YunFang.PhotoGrid/issues?time=last-seven-days&state=open&tag=all")#輸入網址
keyevent("66")#enter

# webhook = "https://open.feishu.cn/open-apis/bot/v2/hook/0e427c76-6ff1-4980-919e-d1e28c9db44c"#iOS
webhook = "https://open.feishu.cn/open-apis/bot/v2/hook/ec0758f7-1e48-4850-b7a3-7e46abe4c276"#測試機器人


day7s = []
day7vs = []
day1s = []
day1vs = []

sleep(15.0)



if poco(text="已登出").exists():
    poco(text="登入").click()
else:
    print("網頁正常")



if poco(text="您並未登入帳戶"):
    poco(text="再試一次").click()
    sleep(5.0)
    poco(text="下一步").click()
    sleep(5.0)
    keyevent("x")
    keyevent("a")
    keyevent("s")
    keyevent("x")
    keyevent("a")
    keyevent("s")
    keyevent("w")
    keyevent("a")
    poco(text="下一步").click()
elif poco(text="驗證您的身分"):
    poco(text="下一步").click()
    sleep(5.0)
    poco(text="登入").click()
    sleep(10.0)
    # keyevent("x")
    # keyevent("a")
    # keyevent("s")
    # keyevent("x")
    # keyevent("a")
    # keyevent("s")
    # keyevent("w")
    # keyevent("a")
    # poco(text="下一步").click()
else:
    print("帳號已登入")
    



#current_date 变量用当前日期和时间作为值，并使用 strftime 方法格式化为字符串。filename 变量则将当前日期和时间拼接到指定文件路径中，形成一个文件名。
current_date1 = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M")
filename1 = "/Users/jadeliu/Desktop/mag/7d_" + current_date1 + ".jpg"  
shot1 = snapshot(filename=filename1, msg="七天的.")  

#這段代碼首先將所有符合條件的對象轉化為一個列表
#通过循环这个列表对,每一个元素调用 "get_text()" 方法来提取它的文本内容，最后存储在变量中。
day_7 = poco(name='android.widget.Button')

day_7_list = [i.get_text() for i in day_7]

day_7_value = poco(name='mat-tab-label-0-0')

day_7_value_list = [i.get_text() for i in day_7_value]


#這段代碼將一個列表 title_list 添加到另一個列表 a_list1 中，作為它的一個元素。
day7s.append(day_7_list)
day7vs.append(day_7_value_list)  


for i in day7s:
    #test2=(i[-2])
    test7=(len(i))
    print (i)
    print ("共撈取",test7,"個數據","\n")
    for element in i:
        if "日至" in element:
            test7 = element
            break
    print ("印出的數據為:",test7,"\n")
    string7 = test7
    string7 = re.sub("已選取的日期範圍","最近七天",string7)
    
for i in day7vs:
    gg=(len(i))
    print (i)
    print ("共撈取",gg,"個數據","\n")
# 遍历列表中的每个元素
for element in i:
    # 使用正则表达式匹配百分比格式的数字
    match = re.search(r'(99.\d+)%', str(element))
    if match:
        # 如果找到匹配项，打印出来
        percentage7 = match.group(1)
        print("提取的百分比:", percentage7)
#if  gg >= 8:#取決於當前手機 Flip3=14 ZenFone5=8
#    test3=(i[4])
#    print("印出的數據為:",test3,"\n")
#else:#取決於當前手機 Flip3=16 ZenFone5=10
#    test3=(i[6])
#     print("印出的數據為:",test3,"\n")
    

poco(name="com.android.chrome:id/home_button").click()#回首頁
poco(name="com.android.chrome:id/search_box_text").set_text("https://console.firebase.google.com/u/0/project/photogrid-42441/crashlytics/app/ios:com.YunFang.PhotoGrid/issues?state=open&time=last-twenty-four-hours&types=crash&tag=all&sort=eventCount")#輸入網址
keyevent("66")#enter

sleep(20.0)


day_1 = poco(name='android.widget.Button')

day_1_list = [i.get_text() for i in day_1]

day_1_value = poco(name='mat-tab-label-0-0')

day_1_value_list = [i.get_text() for i in day_1_value]


day1s.append(day_1_list)
day1vs.append(day_1_value_list)  


current_date = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M")
filename = "/Users/jadeliu/Desktop/mag/1d_" + current_date + ".jpg"  
shot1 = snapshot(filename=filename, msg="一天的")   



for i in day1s:
    #test2=(i[-2])
    test1=(len(i))
    print (i)
    print ("共撈取",test1,"個數據","\n")
    for element in i:
        if "日至" in element:
            test1 = element
            break
    print ("印出的數據為:",test1,"\n")
    string1 = test1
    string1 = re.sub("已選取的日期範圍","過去24小時",string1)
    
for i in day1vs:
    gg=(len(i))
    print (i)
    print ("共撈取",gg,"個數據","\n")
# 遍历列表中的每个元素
for element in i:
    # 使用正则表达式匹配百分比格式的数字
    match = re.search(r'(\d+\.\d+)%', element)
    if match:
        # 如果找到匹配项，打印出来
        percentage = match.group(1)
        print("提取的百分比:", percentage)



# for i in day1s:
#     #test5=(i[-2])
#     test55=(len(i))
#     print(i)
#     print("共撈取",test55,"個數據","\n")
#     for element in i:
#         if "日至" in element:
#             test5 = element
#             break
#     print("印出的數據為:",test5,"\n")
#     string3 = test5
#     string3 = re.sub("已選取的日期範圍","最近24小時",string3)

# for i in day1vs:
#     gg=(len(i))
#     print(i)
#     print ("共撈取",gg,"個數據","\n")
#     for element in i:
#         if "%" in element:
#             test6 = element
#             break


#if  gg >= 7:#等於 #三星Flip3=10 #ZenFone5=7
#    test6=(i[4])
#    print("印出的數據為:",test6,"\n")
#else:
#    test6=(i[6])#三星Flip3=12 #ZenFone5=9
#     print("印出的數據為:",test6,"\n")


for i in range(3):
    home_btn =  poco(name="com.android.chrome:id/home_button")
    if home_btn and home_btn.exists():
        home_btn.click()
        break
    else:
        home_btn.refresh()
        sleep(6.0)

payload_message = {"msg_type": "text","content": {"text":"PG iOS"+"\n"+string1+"\n"+"不受當機影響的使用者："+percentage+"%"}}
headers ={"Content-Type":"application/json"}
response = requests.request("POST", webhook, headers=headers, data=json.dumps(payload_message))

sleep(2.0)

payload_message = {"msg_type": "text","content": {"text":"PG iOS"+"\n"+string7+"\n"+"不受當機影響的使用者："+percentage7+"%"}}
headers ={"Content-Type":"application/json"}
response = requests.request("POST", webhook, headers=headers, data=json.dumps(payload_message))

