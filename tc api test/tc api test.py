# -*- coding: utf-8 -*-
"""
Created on Fri Aug 19 16:03:27 2022

@author: maomao
"""
import requests
import datetime
import time

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
path = '16219555652327.jpg'
event_id = str(int(time.time()*1000))
url = 'https://34.80.33.162:8000/v1/recognition_api/tc_img_upload'
userID = 'test'
event_time = get_crt_time(time.time())
image = open(path,'rb')

files = {'image': ('image.jpg', image, 'image/jpeg')}
data = {'event_id': event_id,'event_time':event_time,'user_id': userID}
x = requests.post(url, data = data ,files=files, verify=False)