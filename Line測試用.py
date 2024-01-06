import pandas as pd
from Testmodule import 證交所產業分類, 資產負債表, 綜合損益表
from datetime import date, datetime
from pandas.core.reshape.pivot import pivot
from linebot.models import *
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot import (
    LineBotApi, WebhookHandler
)
from flask import Flask, request, abort
import os
import re
# -*- coding: utf-8 -*-

# 載入LineBot所需要的套件


app = Flask(__name__)
now_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# # 這是愛德華的token, Channel Secrect, 個人ID:
line_bot_api = LineBotApi('R6xhSVo39d+BwU3uNoU1hozNzq+LGxB0+SaIp/6rsGZz4XebV/eMTKYJPECufCfsQp/+D5Qyud13dDoMFtHiUGLC2iDfO2EjwX7l6+4hno0CL3r2ssnd/W/kPAGixXYqTPNbojiHCfp7v3Gi+GyJAAdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('1d4de1d6d16dc9be4de83f8835479849')
line_bot_api.push_message(
    'Uf7c0d2712c0be085df517184ae2548ac', TextSendMessage(text=f'歡迎來到選股達人，若你準備好了，請輸入開始吧'))

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# 訊息傳遞區塊
##### 基本上程式編輯都在這個function #####
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message = text = event.message.text
    if re.match('開始吧', message):
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage('請問你要怎麼選股?是要系統推薦請輸入1，自己查詢請輸入2?'))
    elif message == '1':
        dataset1 = main()
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text = dataset1))
    elif re.match('2', message):
        line_bot_api.reply_message(event.reply_token, TextSendMessage('系統推薦請輸入1，自己查詢請輸入2'))
    else:
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage('輸入錯誤囉! 系統推薦請輸入1，自己查詢請輸入2'))


# @handler.add(MessageEvent, message=TextMessage)
# def handle_message(event):
#     message = text = event.message.text
#     if re.match('我要選股', message):
#         line_bot_api.reply_message(event.reply_token, TextSendMessage('台積電'))
#     else:
#         line_bot_api.reply_message(event.reply_token, TextSendMessage(message))

def main():
    current_date = date.today()
    user_year = current_date.year
    current_quarter = (current_date.month - 1) // 3 + 1

    if (   # 以金管會規定財報發佈期間為標準，若介於財報尚未發佈期間
        (date(current_date.year, 1, 1) <= current_date <= date(current_date.year, 3, 31)) or
        (date(current_date.year, 4, 1) <= current_date <= date(current_date.year, 5, 15)) or
        (date(current_date.year, 7, 1) <= current_date <= date(current_date.year, 8, 14)) or
        (date(current_date.year, 10, 1) <=
         current_date <= date(current_date.year, 11, 14))
    ):

        # 改成抓上兩季的資料（如果現在是第一季，抓去年第三季資料）
        user_quarter = current_quarter - 2
        if user_quarter <= 0:
            user_quarter += 4
            user_year -= 1

    else:
        user_quarter = current_quarter - 1  # 抓上一季的資料（如果現在是第一季，抓去年第三季）
        if user_quarter <= 0:
            user_quarter += 4
            user_year -= 1

    income_statement = 綜合損益表.綜合損益表by季(user_year, user_quarter)
    balance_sheet = 資產負債表.資產負債表by季(user_year, user_quarter)

    # 兩張table都有獨立的key，利用這兩個key值將兩張table結合
    resultdf = income_statement.merge(balance_sheet, on='Key', how='inner')
    resultdf = resultdf.drop(
        columns=['公司 代號_y', '年度_y', '季別_y', '公司名稱_y'])  # 刪掉重複欄位
    resultdf.rename(columns={'公司 代號_x': '公司代號', '年度_x': '年度',
                    '季別_x': '季別', '公司名稱_x': '公司名稱'}, inplace=True)
    resultdf['公司代號'] = resultdf['公司代號'].astype(str)  # 變更欄位的type，用於merge用
    category = 證交所產業分類.industry()
    resultdf = resultdf.merge(category, how="inner", on="公司代號")

    # dataset1
    # 把resultdf另外用project這個dictionary給複製出來，避免改動到原始爬蟲資料
    project = {}
    project['公司代號'] = resultdf['公司代號']
    project['公司名稱'] = resultdf['公司名稱']
    project['產業別'] = resultdf['產業別']
    project['年度'] = resultdf['年度']
    project['季別'] = resultdf['季別']
    project['基本每股盈餘_EPS'] = resultdf['基本每股盈餘（元）']  # EPS(1)
    project['營業收入'] = resultdf['營業收入']
    project['本期淨利（淨損）'] = resultdf['本期淨利（淨損）']  # 利潤(6)

    project = pd.DataFrame(project)

    # 先將project的年度、季別合併，變成date的形式後排序，之後繪圖座標軸才會正確
    project['Date'] = (project['年度'] + 1911).astype(str) + \
        (project['季別']*3-2).astype(str)
    project['Date'] = pd.to_datetime(project['Date'], format='%Y%m')

    p_time = project  # 複製一個要修改的p_time避免動到原本project
    # 把重複的時間刪掉，因此只會有5個時間從最新(當季)到最舊(前5季)
    p_time = p_time.drop_duplicates(subset=['Date'])
    time_list = []
    for i in range(5):
        # 用for迴圈把每個時間加到time_list
        time_list.append(p_time.iat[i, -1].strftime("%Y-%m-%d"))
    time_list = sorted(time_list, reverse=True)  # 由最新的季別排到最早的季別

    # 處理missing
    project1 = project.dropna(
        subset=['基本每股盈餘_EPS', '營業收入', '本期淨利（淨損）'])  # n=4772
    project1 = project1.groupby(['公司名稱']).agg('count')  # n=958
    project1 = project1[~(project1['基本每股盈餘_EPS'] < 5)]  # n=943
    project1 = pd.merge(project1, project, how='left', suffixes=[
                        "_x", ""], on=['公司名稱'])  # n=4715
    project1 = project1[['產業別', '公司代號', '公司名稱', '基本每股盈餘_EPS',
                         '營業收入', '本期淨利（淨損）', 'Date', '季別', '年度']]  # n=4715

    # exclude1: 2023/Q3>2022/Q3 營收
    p1 = project1[['公司名稱', 'Date', '營業收入']]
    p1.sort_values(by=['公司名稱', 'Date'],)  # 排序資料
    p1 = p1.pivot(index='公司名稱', columns='Date', values='營業收入')  # 轉置表格 #n=943
    p1 = p1[~(p1[time_list[0]] < p1[time_list[4]])]  # n=319
    p1 = pd.merge(p1, project1, how='left', on=['公司名稱'])  # n=1595
    p1 = p1[['產業別', '公司代號', '公司名稱', '基本每股盈餘_EPS',
             '營業收入', '本期淨利（淨損）', 'Date']]  # n=1595

    # exclude2 : 任一季EPS為負數
    p2 = p1[['公司名稱', 'Date', '基本每股盈餘_EPS']]
    p2.sort_values(by=['公司名稱', 'Date'])
    p2 = p2.pivot(index='公司名稱', columns='Date', values='基本每股盈餘_EPS')  # n=319
    for time_ymd in time_list:
        p2 = p2[~(p2[time_ymd] < 0)]  # n=233 用迴圈跑time_list取代固定季別，之後可以擴充更多季別
    p2 = pd.merge(p2, project, how='left', on=['公司名稱'])
    p2 = p2[['產業別', '公司代號', '公司名稱', '基本每股盈餘_EPS',
             '營業收入', '本期淨利（淨損）', 'Date']]  # n=1165

    # exclude3: 2023/Q3>2022/Q3 利潤
    p3 = p2[['公司名稱', 'Date', '本期淨利（淨損）']]
    p3.sort_values(by=['公司名稱', 'Date'])  # 排序資料
    p3 = p3.pivot(index='公司名稱', columns='Date',
                  values='本期淨利（淨損）')  # 轉置表格 #n=233
    p3 = p3[~(p3[time_list[0]] < p3[time_list[4]])]  # n=167
    p3 = pd.merge(p3, project1, how='left', on=['公司名稱'])
    p3 = p3[['產業別', '公司代號', '公司名稱', '基本每股盈餘_EPS',
             '營業收入', '本期淨利（淨損）', 'Date']]  # n=4710

    # 篩選出年收成長前5%支
    p3['公司代號+公司名稱'] = p3['公司代號']+" "+p3['公司名稱']
    dataset1 = p3.pivot(index=['公司代號+公司名稱'], columns='Date', values='營業收入')
    dataset1['季營收成長率(%)'] = round(
        ((dataset1[time_list[0]]-dataset1[time_list[4]])/dataset1[time_list[4]])*100, 2)
    # 排序資料) #排序資料
    dataset1.sort_values(by=['季營收成長率(%)'], ascending=False, inplace=True)
    dataset1 = dataset1.head(int((len(dataset1.axes[0])-1)*0.05))  # n=8
    output1 = ""
    for i in dataset1.index.values:
        output1 += str(i)+"\n"

    return output1

# 主程式
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
