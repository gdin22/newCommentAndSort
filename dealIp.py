import requests
from pymongo import MongoClient
conn = MongoClient('localhost', 27017)
db = conn.self


class DealIp(object):
    def __init__(self):
        self.ip_url = 'http://331935043663215668.standard.hutoudaili.com/?num=1&area_type=3&scheme=1&anonymity=3'

    # 一次只请求一个
    def get_html_returnip(self):
        html = requests.get(self.ip_url)
        ip = html.text
        return ip

    def add_new_and_remove_old(self):
        http = self.get_html_returnip()
        db.ip.remove()
        db.ip.insert_one({'http': http})
        return self.get_ip()

    def get_ip(self):
        try:
            http = db.ip.find_one()['http']
            return http
        except Exception as e:
            print(e)
            return self.add_new_and_remove_old()
