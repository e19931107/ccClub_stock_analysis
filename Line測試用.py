import os
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)

from linebot.exceptions import (
    InvalidSignatureError
)

from linebot.models import *

app = Flask(__name__)

# 必須放上自己的Channel Access Token
line_bot_api = LineBotApi(
    '+6ierndjKCQOOQ3BoF3WwiGhgkhUsLx77uI8wOK6ntAHVHUmDuG8RXBXFmv6U4tzLSwl0Zr2+e/TpfrqRjtVtyeMsTtBgfaOnSAOL5xrsUNABB0bqkmSHwa7tOoHfEtxodjt/7puwwp0nQy3gcl1GwdB04t89/1O/w1cDnyilFU=')
# 必須放上自己的Channel Secret
handler = WebhookHandler('4f216dc67b4ec0e55a3cb9d175ee1c38')

# 以下放入個人ID
line_bot_api.push_message(
    'U1770a65eee08d14a9e5e97e52da41022', TextSendMessage(text='你可以開始了'))

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
    message = TextSendMessage(text=event.message.text)
    line_bot_api.reply_message(event.reply_token, message)


# 主程式
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
