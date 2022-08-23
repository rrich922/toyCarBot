# -*- coding: utf-8 -*-
"""
Created on Mon Aug  8 11:40:38 2022

@author: maomao
"""

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