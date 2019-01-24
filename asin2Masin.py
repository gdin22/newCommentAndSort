import requests
import re
import os
import random
from dealIp import DealIp
import time


class Asin2asin(object):
    """
    这个类用于将子asin转换为母asin
    在类中写入 子asin
    调用getNasub方法 返回母asin
    """
    def __init__(self):
        self.demo_url = 'https://www.amazon.com/dp/'
        self.user_agent = [
            "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
            "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"
        ]

    '''
    def gethtml(self, asin):
        try:
            url = os.path.join(self.asinurl, asin)
            html = requests.get(url, headers={'User-Agent': random.choice(self.user_agent)})
            # html.encoding = html.apparent_encoding
            return html.text
        except:
            pass
    '''

    # 根据url headers 还有proxies代理 进对网页进行获取 设置了如果网页中存在robot检测即有验证码 就进行ip重取 减小ip的损耗
    # 要设置超时时间 要不然肯能会卡住
    def get_html(self, url, headers, proxies, timeout):
        try:
            html = requests.get(url, headers=headers, proxies=proxies, timeout=timeout)
            if html.text.lower().find('robot check') == -1:
                return html.text
            else:
                proxies = self.tranHttp()
                return self.get_html(url, headers=headers, proxies=proxies, timeout=timeout)
        except:
            proxies = self.tranHttp()
            return self.get_html(url, headers=headers, proxies=proxies, timeout=timeout)

    # 解析网页 用正则匹配母asin 返回字符串类型的母asin
    def getMasin(self, asin):
        dealip = DealIp()
        http = dealip.get_ip()
        proxies = {'https': 'http://'+http}

        url = os.path.join(self.demo_url, asin)
        htmltext = self.get_html(url, headers={'user-agent': random.choice(self.user_agent)}, proxies=proxies,
                                 timeout=20)
        print(asin)
        try:
            masin = re.findall('>[0-9A-Z]{10}<', htmltext)[0][1:-1]
            return masin
        except:
            return '1234567890'

    # 在访问网页出现错误的时候 需要对ip进行重新获取然后更新
    # each_time为每次请求api的时间间隔
    # 返回ip
    def tranHttp(self, each_time=5):
        time.sleep(each_time)
        dealip = DealIp()
        http = dealip.add_new_and_remove_old()
        proxies = {'https': 'http://' + http}
        print('切换ip')
        return proxies
