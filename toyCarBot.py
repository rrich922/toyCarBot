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

from utils import get_crt_time

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



from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, ImageMessage
    ,TextSendMessage,ImageSendMessage,TemplateSendMessage
    ,PostbackEvent,PostbackAction,MessageTemplateAction
    ,ButtonsTemplate,
)






CLASSES = ['轉爐石', '其他', '瀝青刨除料',
           '天然骨材', '焚化再生粒料', '電弧爐氧化碴',
           '太陽光電回收玻璃', '太陽光電回收玻璃']

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





@handler.add(MessageEvent, message=ImageMessage)
def handle_message(event):
    global a 
    a = event

    upload_url = 'https://34.80.33.162:8000/v1/recognition_api/tc_img_upload'
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
    x = requests.post(upload_url, data = data ,files=files)
    
    upload = False
    for i in range(5):
        time.sleep(1)
        with conn.cursor() as cursor:
            command = "select event_result,event_value from tc_img_recognition where event_id = "+str(event_id)+";"    
            cursor.execute(command)
            result = cursor.fetchall()
            cursor.close()
            conn.commit()
        if not len(result) or result[0][0]==None:
            print(result)
            time.sleep(1)    
        else:
            upload = True
            break
    if upload:
        print(result)
        value = int(result[0][1]*100)
        if value<50 or result[0][0]==1:
            msg = "你不要騙我，這是你亂拍的對吧XD"
        else:
            msg = "這看起來有"+str(value)+"%像是"+str(CLASSES[result[0][0]])
    else:
        msg = "server delay"
    line_bot_api.reply_message(
         event.reply_token,
         TextSendMessage(text=msg))
    

    
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text
    if msg in dialogs:
        rtMsg = dialogs[msg].replace('\\n','\n')
    else:
        rtMsg = ' https://www.youtube.com/watch?v=TBKhml1qVLM'
    

    template = TemplateSendMessage(
                            alt_text='Buttons template',
                            template=ButtonsTemplate(
                                title='Menu',
                                text='請選擇地區',
                                actions=[
                                    MessageTemplateAction(
                                        label='台北市',
                                        text='台北市'
                                    ),
                                    MessageTemplateAction(
                                        label='台中市',
                                        text='台中市'
                                    ),
                                    MessageTemplateAction(
                                        label='高雄市',
                                        text='高雄市'
                                    ),
                                    PostbackAction(
                                        label='postback2',
                                        #display_text='postback text2',
                                        data='action=buy&itemid=2'
                                        ) 
                                ]
                            )
                        )
    
    
    line_bot_api.reply_message(
            event.reply_token,
            [TextSendMessage(text=rtMsg),template])
            #TextSendMessage(text=rtMsg))
            
@handler.add(PostbackEvent)
def handle_postback(event):
    action = event.postback.data
    line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=action))    

if __name__ == '__main__':

    app.run(port=5000, debug=False)
