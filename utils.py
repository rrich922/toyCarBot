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
    def __init__(self,):
        self.CLASSES = ['轉爐石', '其他', '瀝青刨除料',
           '天然骨材', '焚化再生粒料', '電弧爐氧化碴',
           '太陽光電回收玻璃', '太陽光電回收玻璃']
        
        self.replyText = os.listdir('replyText')

    def imageEvent(self,upload,result):
        if upload:
            value = int(result[1]*100)
            if value<50 or result[0]==1:
                msg = "你不要騙我，這是你亂拍的對吧XD"
            else:
                msg = "這看起來有"+str(value)+"%像是"+str(self.CLASSES[result[0]])
        else:
            msg = "server delay"
        return msg
    
    def textEvent(self,text,msg,dialogs):
        if msg in dialogs:
            rtMsg = dialogs[msg].replace('\\n','\n')
            if rtMsg in self.replyText:
                reply = open('replyText/'+rtMsg, 'r').readlines()
                rtMsg = ''.join(reply)
        else:
            rtMsg = ' https://www.youtube.com/watch?v=TBKhml1qVLM'
        
        
    