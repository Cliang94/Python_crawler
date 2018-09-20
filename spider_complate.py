import requests
from fake_useragent import UserAgent
from retrying import retry
import hashlib
import queue
import re
from urllib import robotparser
from urllib.parse import urlparse,urldefrag,urljoin
from datetime import datetime
import time
from ad_mongodb.mongo_cache import MongoCache
from random_proxies import random_proxies

MAX_DEP = 2


def get_robots(url):
    """

    :param url:
    :return:
    """
    rp = robotparser.RobotFileParser()
    url = "http://" + urlparse(url).netloc
    rp.set_url(urljoin(url,'robots.txt'))
    rp.read()
    return rp

def extractor_url_lists(html_content):
    """

    :param html_content:
    :return:
    """

    url_regex = re.compile('<a[^>]+href=["\'](.*?)["\']',re.I)
    return url_regex.findall(html_content.decode('gbk'))

def save_url(html_conten,url_str):
    """

    :param html_conten:
    :param url_str:
    :return:
    """
    md5 = hashlib.md5()
    md5.update(html_conten)
    file_path = './download/' + gen_html_name(url_str)
    with open(file_path,'wb') as f:
        f.write(html_conten)


def gen_html_name(url_str):
    path = urlparse(url_str).path
    path_array = path.rsplit('/',1)
    return path_array[1]







class CrawlerCOmmon(object):
    """
    通用爬虫下载
    """

    def __init__(self,init_url):

        __ua = UserAgent()

        self.headers = {"User-Agent":__ua.random}
        self.seed_url = init_url

        self.crawler_queue = queue.Queue()
        self.crawler_queue.put(init_url)
        self.rp = get_robots(init_url)
        self.throttle = Throttle(5.0)
        self.mcache = MongoCache()
        self.visited = {init_url:0}


        import requests
        self.sessions_login = requests.session()



    @retry(stop_max_attempt_number=3)
    def retry_download(self,url_str,data,method,proxies):

        """

        :param url_str:
        :param data:
        :param method:
        :param proxies:
        :return:
        """
        if method == "POST":
            result = requests.post(url_str,data=data,headers=self.headers,proxies=proxies)
        else:
            result = requests.get(url_str,hearders=self.headers,proxies=proxies)
        assert result.status_code == 200
        return result.content


    def download(self,url_str,data=None,method="GET",proxies = {}):
        """



        :param url_str:
        :param data:
        :param method:
        :param proxies:
        :return:
        """
        print('downlaod::::',url_str)
        try:
            result = self.retry_download(url_str,data,method,proxies)
        except requests.HTTPError as e:
            print(e)
            result = None
        return result

    def nomalize(self,url_str):
        """

        :param url_str:
        :return:
        """

        real_url, _ = urldefrag(url_str)
        return urljoin(self.seed_url,real_url)





    def run(self):
        """

        :return:
        """
        while not self.crawler_queue.empty():
            url_str = self.crawler_queue.get()
            if self.rp.can_fetch(self.headers['User-Agent'],url_str):
                self.throttle.wait_url(url_str)
                depth = self.visited[url_str]

                if depth < MAX_DEP:
                    html_content = self.download(url_str,proxies=random_proxies())

                    if html_content is not None:
                        save_url(html_content,url_str)

                    url_list = extractor_url_lists()

                filter_urls = [link for link in url_list if re.search('/(1111)',link)]

                for url in filter_urls:
                    real_url = self.nomalize(url)

                    if real_url not in self.visited:
                        self.visited[real_url] = depth + 1
                        self.crawler_queue.put(real_url)
            else:
                print('robots.txt 禁止下载',url_str)








class Throttle(object):
    """
    下载限流器
    """

    def __init__(self,delay):
        """

        :param delay:
        """
        self.domains = {}
        self.delay = delay

    def wait_url(self,url_str):
        """

        :param url_str:
        :return:
        """
        domain_url = urlparse(url_str).netloc
        last_accessed = self.domains.get(domain_url)

        if self.delay > 0 and last_accessed is not None:
            sleep_interval = self.delay - (datetime.now() - last_accessed).seconds
            if sleep_interval > 0:
                time.sleep(sleep_interval)

        self.domains[domain_url] = datetime.now()




































