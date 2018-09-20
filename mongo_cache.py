import requests
import zlib # 压缩数据
import lxml.html
from pymongo import MongoClient
import pickle # 对象序列化
from datetime import datetime,timedelta # 设置缓存超时时间间隔
from bson.binary import Binary  # mongodb 存储二进制的类型


class MongoCache:
    """
    数据库缓存
    """
    def __init__(self,client=None,expires=timedelta(days=30)):
        """
        初始化函数
        :param client:数据库连接
        :param expires: 超时时间
        """
        self.client = MongoClient("localhost",27017)
        self.db = self.client.cache  # 创建一个名为cache的数据库
        web_page = self.db.webpage   # 获取webpage 这个表 （collection）

        # 创建timstamp 索引，设置超时时间为30天（会自动转化为秒）
        self.db.webpage.create_index('timstamp',expireAfterSeconds=expires.total_seconds())

    def __setitem__(self, key, value):
        """
        向数据库添加一条缓存（数据）
        :param key: 缓存关键字
        :param value: 缓存内容
        :return:
        """
        # 将数据使用pickle序列化，在使用zlib压缩，最后转化为Binary格式，使用格林威治时间
        record = {"result":Binary(zlib.compress(pickle.dumps(value))),'timestamp':datetime.utcnow()}
        # 使用下载url作为key，存入系统默认生成的_id 字段，存入数据库中
        self.db.webpage.update({'_id':key},{'$set':record},upsert=True)

    def __getitem__(self, item):
        """
        将缓存数据按照item作为key取出（key仍然是下载的url）
        :param item:
        :return:
        """

        record = self.db.webpage.find_one({'_id':item})
        if record:
            return pickle.loads(zlib.decompress(record["result"]))
        else:
            raise KeyError(item + "does not exist")

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
        self.db.webpage.drop()
