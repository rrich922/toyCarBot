# -*- coding: utf-8 -*-
"""
Created on Mon Aug  8 11:40:38 2022

@author: maomao
"""

import datetime
import time
import json
import pymysql
import os
from linebot.models import (
    TemplateSendMessage,
    MessageTemplateAction,
    ButtonsTemplate,
    TextSendMessage,
)
def get_crt_time(timestamp):
    """
        return current time
    """
    dt = datetime.datetime.fromtimestamp(int(timestamp)//1000)
    '''
    d = datetime.datetime.utcnow()
    ts = calendar.timegm(d.timetuple())
    crt_time = "%s" % datetime.datetime.fromtimestamp(ts)
    '''
    formatted_month = "%02d" % dt.month
    formatted_day = "%02d" % dt.day
    formatted_hour = "%02d" % dt.hour
    formatted_minute = "%02d" % dt.minute
    formatted_second = "%02d" % dt.second
    crt_time = "%s-%s-%s %s:%s:%s" % (dt.year, formatted_month, formatted_day, formatted_hour, formatted_minute,
                                         formatted_second)

    return crt_time

class DBOperation():
    def __init__(self,settingFile='dbSetting.json',maxRetry=3,sleep=0.5):
        with open(settingFile) as f:
            self.db_settings = json.load(f)
        self.maxRetry = maxRetry
        self.sleep = sleep
    def queryResult(self,event_id):
        upload = False
        conn = pymysql.connect(**self.db_settings)
        conn.ping(reconnect=True)
        for i in range(self.maxRetry):
            time.sleep(self.sleep)
            with conn.cursor() as cursor:
                command = "select event_result,event_value from tc_img_recognition where event_id = "+str(event_id)+";"  
                cursor.execute(command)
                result = cursor.fetchall()
                cursor.close()
                conn.commit()
            if not len(result) or result[0][0]==None:
                print(result)    
            else:
                upload = True
                break
        conn.close()
        result = result[0] if upload else None
        return result, upload
    
class MsgGenerator():
    def __init__(self,dialogs):
        self.CLASSES = ['轉爐石', '瀝青刨除料',
           '天然骨材', '焚化爐再生粒料', '電弧爐氧化碴',
           '太陽光電回收玻璃', '水淬高爐石']
        
        self.Material = ['轉爐石', '瀝青刨除料', '天然骨材',
           '焚化爐再生粒料', '電弧爐氧化碴', '太陽光電回收玻璃',
           '水淬高爐石']
        
        self.replyText = os.listdir('replyText')
        self.dialogs = dialogs


    def templateGenerator(self,material,text='請點選材料查看更多'):
        actions = []
        for m in material:
            action = MessageTemplateAction(
                                    label= m,
                                    text= m
                                    )
            actions.append(action)
        
        template = TemplateSendMessage(
                            alt_text='Buttons template',
                            template=ButtonsTemplate(
                                title='常用的循環材料如下',
                                text=text,
                                actions=actions
                            )
                        )
        return template
    
    def imageEvent(self,upload,result):
        if upload:
            value = int(result[1]*100)
            if value<25:
                msg = TextSendMessage(text="你不要騙我，這是你亂拍的對吧XD")
                return msg
            else:
                msg = "這看起來有"+str(value)+"%像是"+str(self.CLASSES[result[0]])
                msg = TextSendMessage(text=msg)
                intro = self.textEvent(self.CLASSES[result[0]])
                return msg,intro
        else:
            msg = TextSendMessage(text="server delay")
            return msg
    
    def textEvent(self,msg):
        if msg in self.dialogs:
            rtMsg = self.dialogs[msg].replace('\\n','\n')
            if rtMsg[0:2] == 'SR':
                rtMsg = [self.templateGenerator(self.Material[0:4]),self.templateGenerator(self.Material[4:])]
                return rtMsg
            elif rtMsg in self.replyText:
                reply = open('replyText/'+rtMsg, 'r').readlines()
                rtMsg = ''.join(reply)
                return TextSendMessage(text=rtMsg)
        else:
            rtMsg = '其他未設定對話,預設回應區'
            return TextSendMessage(text=rtMsg)
            
        
    
        
        
    