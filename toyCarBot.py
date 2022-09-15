# -*- coding: utf-8 -*-
"""
Created on Tue Jun  7 10:02:01 2022

@author: maomao
"""

# import os
# from argparse import ArgumentParser
# from utils.misc import baseParser
# from models.apis.image_recognition import ImageDetection
# from models.detr import buildInferenceModel
import csv
import json
import time
import requests

from utils import get_crt_time,DBOperation,MsgGenerator

from flask import Flask, request, abort
app = Flask(__name__)


from linebot import (
    LineBotApi, WebhookHandler
)

with open('token.json') as f:
    token = json.load(f)
line_bot_api = LineBotApi(token['api'])
handler = WebhookHandler(token['webhook'])


import pymysql
with open('dbSetting.json') as f:
    db_settings = json.load(f)
conn = pymysql.connect(**db_settings)
conn.ping(reconnect=True)

with open('ip.json') as f:
    ip = json.load(f)['ip']

from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, ImageMessage
    ,TextSendMessage,ImageSendMessage,TemplateSendMessage
    ,PostbackEvent,PostbackAction,MessageTemplateAction
    ,ButtonsTemplate,
)


with open('dialog.csv', encoding='utf-8-sig') as csvfile:
  # 讀取 CSV 檔內容，將每一列轉成一個 dictionary
  rows = csv.reader(csvfile)
  dialogs = dict([row for row in rows])




@app.route("/", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    #print(body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'




dbOperation = DBOperation()
msgGenerator = MsgGenerator()   
@handler.add(MessageEvent, message=ImageMessage)
def handle_message(event):

    upload_url = 'https://'+ip+':8000/v1/recognition_api/tc_img_upload'
    userID = event.source.user_id
    event_time = get_crt_time(event.timestamp)
    event_id = event.message.id
    content = line_bot_api.get_message_content(event_id)    
    
    path = 'Image/' + event.message.id + '.jpg'
    with open(path, 'wb') as fd:
        for chenk in content.iter_content():
            fd.write(chenk)    
    
    image = open(path,'rb')

    files = {'image': ('image.jpg', image, 'image/jpeg')}
    data = {'event_id': event_id,'event_time':event_time,'user_id': userID}
    try:
        x = requests.post(upload_url, data = data ,files=files, verify=False)
        result, upload = dbOperation.queryResult(event_id)
        msg = msgGenerator.imageEvent(upload, result)
    except:
        msg = "伺服器維修中,暫無回應"
    line_bot_api.reply_message(
         event.reply_token,
         TextSendMessage(text=msg))
    

    
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text
    rtMsg = msgGenerator.textEvent(msg, dialogs)



    
    line_bot_api.reply_message(
            event.reply_token,
            rtMsg)
            #TextSendMessage(text=rtMsg))
            
@handler.add(PostbackEvent)
def handle_postback(event):
    action = event.postback.data
    line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=action))    

if __name__ == '__main__':
    from waitress import serve
    serve(app, host="0.0.0.0", port=5002)
    #app.run(port=5002, debug=False)
