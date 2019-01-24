import requests
from bs4 import BeautifulSoup
import json
import re
import random
from dealIp import DealIp
import time
requests.packages.urllib3.disable_warnings()


class ComAndSort(object):
    def __init__(self):
        self.user_agent = [
            "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
            "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"
        ]

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

    # 根据处理过的response 即为soup进行解析
    # 得到评论数 调用得到排行
    def get_comment_num_sort(self, url):
        dealip = DealIp()
        http = dealip.get_ip()
        proxies = {'https://': http}

        htmltext = self.get_html(url, headers={'user-agent': random.choice(self.user_agent)}, proxies=proxies,
                                 timeout=20)
        soup = BeautifulSoup(htmltext, 'lxml')
        # print(soup)
        int_sort_num = self.get_first_sort(soup)
        comment_num = int(soup.select('#cm-cr-dp-review-header > h3 > span')[0].text.split(' ')[-2])
        return int_sort_num, comment_num

    # 根据处理过的response 进行解析
    # 用正则处理取得的数 具体实现 得到排行的数
    def get_first_sort(self, soup):
        sort = soup.select('#SalesRank')
        text = sort[0].text
        sort_num = text.split('#')[1].split(' ')[0]
        sort_list = re.findall(r'\d', sort_num)
        int_sort_num = int(''.join(sort_list))
        return int_sort_num

    # 获取最新的评论时 不可使用get
    # 还要使用https ssl加密 可选择False
    # pagesize 即1页 最多只能50条每页
    def get_sort_comment(self, asin='B0755BYDD9', num=10):
        url = 'https://www.amazon.com/hz/reviews-render/ajax/reviews/get/ref=cm_cr_getr_d_paging_btm_2'
        headers = {'User-Agent': random.choice(self.user_agent)}
        data = {
            'sortBy': 'recent',
            'reviewerType': 'all_reviews',
            'pageNumber': '1',
            'shouldAppened': 'undefined',
            'deviceType': 'desktop',
            'reftag': 'cm_cr_getr_d_paging_btm_3',
            'pageSize': str(num),
            'asin': asin,
            'scope': 'reviewsAjax6'
        }
        html = requests.post(url, headers=headers, params=data, verify=False)
        text = json.dumps(html.text)
        starList = re.findall(r'title=\\\\\\"(.*?) out of 5 stars', text)
        sizeList = re.findall(r'>Size: (.*?)<', text)
        colorList = re.findall(r'>Color: (.*?)<', text)
        return {'star': starList, 'size': sizeList, 'color': colorList}

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
