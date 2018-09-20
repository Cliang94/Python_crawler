from random import choice,randint
from fake_useragent import UserAgent
from pymongo import MongoClient
from bson.binary import Binary
from datetime import datetime
import lxml.html
import requests
import time
import pickle


class MongoCache_Proxies(object):
    """
    数据库缓存
    """
    def __init__(self,client=None):
        """
        初始化函数
        :param client: 数据库链接
        """

        self.client = MongoClient('localhost',27017)
        self.db = self.client.IP_Proxies
        ip_proxies_ = self.db.Proxies
        self.db.Proxies.create_index('time')
        if self.db.Proxies.find().count() == 0:
            record = {"result": Binary(pickle.dumps({'http': 'http://114.113.126.82:80'})), 'time': datetime.now()}
            self.db.Proxies.update({'_id': 1}, {'$set': record}, upsert=True)


    def __setitem__(self, key, value):
        """
        向数据库中添加数据
        :param key: 缓存关键字
        :param value: 缓存内容
        :return:
        """
        record = {"result":Binary(pickle.dumps(value)),'time':datetime.now()}
        self.db.Proxies.update({'_id':key},{'$set':record},upsert=True)
    def __getitem__(self, item):
        """
        将缓存数据按照item作为key取出
        :param item:
        :return:
        """
        record = self.db.Proxies.find_one({'_id':item})
        if record:
            return pickle.loads(record['result'])
        else:
            raise KeyError(str(item) + 'does not exist')


    def __contains__(self, item):
        """
        当调用in，not in 会调用该方法判断对应网址是否在数据库的缓存中
        :param item: 下载的url链接
        :return:
        """
        try:
            self[item]
        except KeyError:
            return False
        else:
            return True

    def clear(self):
        self.db.Proxies.drop()

    def count_all(self):
        return self.db.Proxies.find().count()






class Random_Proxies(object):
    """
    从指定代理网址下载代理ip
    """

    def __init__(self):
        """
        初始化下载
        """
        _au = UserAgent()
        # 快代理 国内高匿代理
        self.url_base = 'https://www.kuaidaili.com/free/inha/{}/'
        # 快代理 国内普通代理
        # self.url_base = 'https://www.kuaidaili.com/free/intr/{}/'
        #
        self.headers = {'UserAgent':_au.random}
        self.db = MongoCache_Proxies()

    def url_lists(self):
        """
        下载列表
        """
        return [self.url_base.format(i) for i in range(1,35)]

    def download_html(self,url_str):
        """
        下载页面
        :param url_str:
        :return:
        """
        result = requests.get(url_str,headers=self.headers,proxies=self.random_proxies())
        return result.content.decode('utf-8')

    def parse_lxml(self,html_str):
        """
        提取ip并拼接为指定格式
        :param html_str:
        :return:
        """
        ip_list = []
        html = lxml.html.fromstring(html_str)
        ip_data = html.xpath('//table/tbody/tr/td[@data-title="IP"]/text()')
        port_data = html.xpath('//table/tbody/tr/td[@data-title="PORT"]/text()')
        if not ip_data or not port_data:
            raise KeyError('ip list or port list is None!')

        for i in range(len(ip_data)-1):
            ip_str = ip_data[i] + ':' + port_data[i]
            ip_list.append(ip_str)
        return ip_list

    def save_ip_str(self,ip_list):
        """
        保存数据
        :return:
        """
        id_ = self.db.count_all()
        for i in ip_list:
            id_ += 1
            dict_ = {"http":"http://" + i}
            self.db[id_] = dict_

    def download(self):
        url_lists = self.url_lists()
        for i in url_lists:
            print('开始下载::::::', i)
            time.sleep(randint(2,5))
            html_str = self.download_html(i)
            ip_list = self.parse_lxml(html_str)
            self.save_ip_str(ip_list)
        print('下载完成')

    def random_proxies(self):
        return self.db[randint(1,self.db.count_all())]

def random_proxies():
    """
    生成随机的proxies
    :return: 随机的proxies 字典格式
    """
    self = Random_Proxies()
    return self.db[randint(1,self.db.count_all())]


#
# def randomproxies:
#



    # return {"http": "http://" + choice(r)}

if __name__ == '__main__':
    # pass


    cc = Random_Proxies()
    # cc.db.clear()
    # cc.download()
    # print(cc.db[490])
    # print(type(cc.random_proxies()))
    for i in range(50):
        print(cc.random_proxies())
        # print(type(cc.random_proxies()))