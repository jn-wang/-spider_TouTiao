import requests
import re
import json
import random
import time
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import pymongo
from toutiao_config import *
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)  ###禁止提醒SSL警告
import execjs

class toutiao(object):

    def __init__(self, url):
        self.url = url
        self.s = requests.session()
        headers = {
                   'Accept': '*/*',
                   'Accept-Language': 'zh-CN',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; .NET4.0C; .NET4.0E; .NET CLR 2.0.50727; .NET CLR 3.0.30729; .NET CLR 3.5.30729; InfoPath.3; rv:11.0) like Gecko',
                   'Connection': 'Keep-Alive',
                   }
        self.s.headers.update(headers)
        self.channel = re.search('ch/(.*?)/', url).group(1)

    def get_js(self):
        f = open(r"E:\SourseCode_JN\爬虫\爬今日头条\toutiao.js", 'r', encoding='UTF-8')  ##打开JS文件
        line = f.readline()
        htmlstr = ''
        while line:
            htmlstr = htmlstr + line
            line = f.readline()
        ctx = execjs.compile(htmlstr)
        return ctx.call('get_as_cp_signature')

    def closes(self):
        self.s.close()

    def save_to_mongo(self,info):
        client = pymongo.MongoClient(MONGO_URL)
        db = client[MONGO_DB]
        if db[MONGO_TABLE].insert(info):
            print('存储到MONGODB成功', info)
            return True
        return False

    def getdata(self):  # 获取数据
        req = self.s.get(url=self.url, verify=False)
        headers = {'referer': self.url}
        max_behot_time = '0'
        self.s.headers.update(headers)
        for i in range(0, 20):  ##获取页数
            Honey = json.loads(self.get_js())
            eas = Honey['as']
            ecp = Honey['cp']
            signature = Honey['_signature']

            url = 'https://www.toutiao.com/api/pc/feed/?category={}&utm_source=toutiao&widen=1&max_behot_time={}' \
                  '&max_behot_time_tmp={}&tadrequire=true&as={}&cp={}&_signature={}'.format(
                        self.channel, max_behot_time, max_behot_time, eas, ecp, signature)

            req = self.s.get(url=url, verify=False)
            time.sleep(random.random() * 2 + 2)
            # print(req.text)
            # print(url)
            j = json.loads(req.text)
            print(j['data'])
            for i in j['data']:
                info = {
                    'image_url':'https:'+i['image_url'],
                    'title':i['title'],
                    'source':i['source'],
                    'media_url':'https://www.toutiao.com'+i['media_url'],
                    'media_avatar_url':'https:'+i['media_avatar_url'],
                    'source_url':'https://www.toutiao.com'+i['source_url'],
                    'middle_image':i['middle_image'],
                    'image_list':i['image_list']
                }
                # self.save_to_mongo(info)
                print(info)

if __name__ == '__main__':
    url = 'https://www.toutiao.com/ch/gallery_old_picture/'
    t = toutiao(url)
    t.getdata()
    t.closes()