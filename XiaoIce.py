# -*- coding: UTF-8 -*-
import requests
import random
import time
import json
import re
import os
import WeiBo
from ResponseResult import XBResult

accountHeaders={}
oldId=0
prevMsg=""

def StoreHeaders():
    global accountHeaders
    fp=open('headers.txt','w')
    for i in accountHeaders:
        fp.write("%s:%s\n"%(i,accountHeaders[i]))
    fp.close()

def LoadHeaders():
    global accountHeaders
    fp=open("headers.txt",'r')
    line = fp.readline().strip()
    while line:
        key = line.split(":")[0]
        accountHeaders[key] = line[len(key)+1:].strip()
        line = fp.readline().strip()            
    fp.close()

def Init():
    global accountHeaders,oldId
    LoadHeaders()
    while True:
        try:
            t=str(time.time())
            requestUrl='https://weibo.com/aj/message/getbyid?ajwvr=6&uid=5175429989&count=1&_t=0&__rnd=%s'%t
            req=requests.get(requestUrl,headers=accountHeaders)
            req.encoding='utf8'
            temp=json.loads(req.text)
            oldId=int(temp['data']['oldid'])
            return True
        except:
            accountHeaders=WeiBo.GetChattingHeaders()
            StoreHeaders()
            continue
    
        

def GetReply():
    global accountHeaders,oldId
    while(True):
        t=str(time.time())
        requestUrl='https://weibo.com/aj/message/getbyid?ajwvr=6&uid=5175429989&count=1&_t=0&__rnd=%s'%t
        req=requests.get(requestUrl,headers=accountHeaders)
        req.encoding='utf8'
        #print req.text
        res=XBResult()
        try:
            temp=json.loads(req.text)
            if int(temp['data']['oldid'])<=oldId:#消息重复，重新获取
                time.sleep(0.3)
                continue
            regexMatch=re.findall('<p class="page">(.*?)</p>',temp['data']['html'])
            
            #print content
            if len(regexMatch)==0:
                res.type='image'
                content=re.findall('<img src="(.*?)"',temp['data']['html'])
                if len(content)==0:
                    res.type='error'
                    return res
                #res.content=content[0]#略缩图
                res.content=content[1]#大图
            else:
                #print content
                #print temp['data']['html']
                content=re.sub('<img(.*?)>',' ',regexMatch[0])
                content=content.encode('utf8')
                if content==prevMsg:
                    time.sleep(0.3)
                    continue
                res.content=content
            #print content
            oldId=int(temp['data']['oldid'])
            return res
        except:
            res.type='error'
            return res
        finally:
            pass
        pass

def ChatWithXB(msg):
    global prevMsg
    prevMsg=msg
    t=str(time.time())
    formData={'location':'msgdialog',
                'module':'msgissue',
                'style_id':'1',
                'text':msg,
                'uid':5175429989,
                'tovfids':'',
                'fids':'',
                'el':'[object HTMLDivElement]',
                '_t':'0'
                }
    requestUrl='https://weibo.com/aj/message/add?__rnd=%s'%t
    req=requests.post(requestUrl,data=formData,headers=accountHeaders)
    #print req.text

def GetResponse(msg):
    ChatWithXB(msg.encode('utf8'))
    return GetReply()

def GetImage(url):
    global accountHeaders
    content=requests.get('https:'+url,headers=accountHeaders)
    fileName='temp\\'+url[url.index('?')+1:]
    #print fileName
    fp=open(fileName,'wb')
    fp.write(content.content)
    fp.close()
    return fileName

if __name__=='__main__':
    Init()
    while True:
        input=raw_input().decode('gb2312').encode('utf8')
        ChatWithXB(input)
        res=GetReply()
        if res.type=='text':
            print u'[小冰]:'+res.content.decode('UTF-8').encode('GBK')
        elif res.type=='image':
            print u'[小冰]:图片回复:%s'%res.content.decode('UTF-8').encode('GBK')
            GetImage(res.content)
        #print 'type:%s content:%s'%(res.type,res.content)