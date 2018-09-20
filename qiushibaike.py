import requests


class Qiushi:

    def __init__(self):
        """
        初始化操作，完成必要设置
        """

        self.url_base = "https://www.qiushibaike.com/8hr/page/{}/"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
        }
        self.proxies = {'proxies':'http://185.22.174.65:9062'}


    def url_lists(self):
        """
        生成下载列表
        :return: 下载列表
        """
        return [self.url_base.format(i) for i in range(1,10)]

    def download_url(self,url_str):
        """
        获取下载内容
        :param url_str: 下载地址
        :return: 下载的内容 content格式
        """

        result = requests.get(url_str,headers=self.headers,proxies=self.proxies)
        return result.content

    def save_result(self,result,page_num):
        """
        保存结果
        :param result: 下载的结果
        :param page_num: 下载的页码
        :return: None
        """
        file_dir = './download/糗事百科-第{}页.html'.format(page_num)
        with open(file_dir,'wb') as f:
            f.write(result)

    def run(self):
        url_lists = self.url_lists()
        for url_str in url_lists:
            result_content = self.download_url(url_str)
            p_num = url_lists.index(url_str)+1
            self.save_result(result_content,p_num)
        print('下载结束')


if __name__ == '__main__':
    qiubai = Qiushi()
    qiubai.run()