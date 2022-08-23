# -*- coding: utf-8 -*-
"""
Created on Tue Jul 12 15:55:53 2022

@author: maomao
"""

import requests
args = {'usr_id': 'test','passwd':'test'}
res = requests.post('https://35.201.147.170:8000/login',data=args,verify = False)
print(res.text)