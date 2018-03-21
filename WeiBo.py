#coding:utf-8
import requests
import random
import time
import json
import re
import os


def DownLoadLoginImage(url):#下载登录二维码
    content=requests.get(url)
    fp=open("login.png",'wb')
    fp.write(content.content)
    fp.close()

loginALT=""


def GetQRCode():#获取登录二维码链接
    global qrid
    url1='https://login.sina.com.cn/sso/qrcode/image?entry=weibo&size=180&callback=STK_%s'
    QRCodeTime=str(time.time())
    html1=requests.get(url1%QRCodeTime)
    html1.encoding='utf8'
    # print html1.text
    imgUrl=re.findall('"image":"(.*?)"',html1.text)[0].encode('utf8')
    imgUrl=imgUrl.replace("\/","/")[2:]
    qrid=re.findall('"qrid":"(.*?)"',html1.text)[0].encode('utf8')
    #print imgUrl
    return imgUrl

def WaitForScan(qrid):#等待扫码，返回真假
    global loginALT
    while(True):
        url='https://login.sina.com.cn/sso/qrcode/check?entry=weibo&qrid=%s&callback=STK_%s'
        req=requests.get(url%(qrid,str(time.time())))
        req.encoding='utf8'
        #print req.text
        state=re.findall('"msg":"(.*?)"',req.text)[0]
        if state=='\u6210\u529f\u626b\u63cf\uff0c\u8bf7\u5728\u624b\u673a\u70b9\u51fb\u786e\u8ba4\u4ee5\u767b\u5f55':
            print '扫码成功，请确认登录'
        elif state=='succ':
            print '登录成功'
            loginALT=re.findall('"alt":"(.*?)"',req.text)[0].encode('utf8')
            return True
        elif state=='\u672a\u4f7f\u7528':
            pass

        else:
            print '扫码失败'
            return False

        time.sleep(1)

loginCookies=None
SUB=""
def Login():#登录
    global loginALT,pcid,QRCodeTime,SUB
    requestUrl='https://login.sina.com.cn/sso/login.php?entry=weibo&returntype=TEXT&crossdomain=1&cdult=3&domain=weibo.com&alt=%s&savestate=30&callback=STK_%s'
    t=str(int(time.time()))
    requestUrl=requestUrl%(loginALT,t)
    #print requestUrl
    req=requests.get(requestUrl)
    #req.encoding='unicode'
    loginCookies=req.headers['Set-Cookie']
    #print loginCookies
    SUB=re.findall('SUB=(.*?);',loginCookies)[0]
    #print SUB


def GetChattingHeaders():#获取和微软小冰聊天所需的https headers
    imgUrl=GetQRCode()
    DownLoadLoginImage('http://'+imgUrl)
    os.system("login.png")
    WaitForScan(qrid)
    Login()
    result={
        'Accept':'*/*',
        'Accept-Encoding':'gzip, deflate, br',
        'Accept-Language':'zh-CN,zh;q=0.9',
        'Cache-Control':'no-cache',
        'Connection':'keep-alive',
        'Content-Type':'application/x-www-form-urlencoded',
        'Cookie':'SUB=',
        'Host':'weibo.com',
        'Pragma':'no-cache',
        'Referer':'https://weibo.com/message/history?uid=5175429989&name=%E5%B0%8F%E5%86%B0',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.167 Safari/537.36',
        'X-Requested-With':'XMLHttpRequest'
    }
    result['Cookie']='SUB='+SUB
    loginHeaders=result
    return result



if __name__=='__main__':
    print GetChattingHeaders()