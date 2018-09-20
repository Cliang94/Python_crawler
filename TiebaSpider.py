import requests
from threading import Thread

class TiebaSpider(Thread):
    def __init__(self, tieba_name_crawl):
        """
        初始化必要参数，完成基础设置
        """
        super(TiebaSpider, self).__init__()
        self.tieba_name = tieba_name_crawl
        self.url_base = "https://tieba.baidu.com/f?kw=" + tieba_name_crawl + "&ie=utf-8&pn={}"
        self.headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
                        }
        self.proxies = {"http": "http://61.135.217.7:80"}
    def make_url_lists(self):
        """
        生成下载列表
        :return: 下载列表
        """

        return [self.url_base.format(i) for i in range(1,5,2)]

    def download_url(self, url_str):
        """
        使用requests get 方法下载指定页面，并返回结果
        :param url_str: 下载链接
        :return: 下载结果
        """

        result = requests.get(url_str,headers = self.headers,proxies=self.proxies)
        return result.content

    def save_result(self, result, page_num):
        """
        存储下载内容

        :param result:  下载的结果
        :param page_num: 下载的页码
        :return: 下载内容
        """
        # with open("./download/"+self.tieba_name+str(page_num)+".html",'wb') as f:
        #     result = result.encode('utf-8')
        #     f.write(result)
        file_path = "./download/{}-第{}页.html".format(self.tieba_name,page_num)
        with open(file_path,'wb') as f:
            f.write(result)


    def run(self):
        """
        下载主线程，实现主要下载逻辑
        :return:
        """
        url_lists = self.make_url_lists()
        for url_str in url_lists:
            result_str = self.download_url(url_str)
            p_num = url_lists.index(url_str) + 1
            self.save_result(result_str,p_num)
        print('下载成功')

if __name__ == '__main__':
    tieba_spider = TiebaSpider('lol')
    tieba_spider.run()












