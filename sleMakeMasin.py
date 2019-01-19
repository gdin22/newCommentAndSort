from selenium import webdriver
from pymongo import MongoClient
import re
import time

conn = MongoClient('localhost', 27017)
db = conn.followsell
asinDict = db.asin.find_one()['asin']
asinList = list(asinDict.keys())

allList = []
driver = webdriver.Chrome()

demo_url = 'https://www.amazon.com/dp/%s'

i = 0
for asin in asinList:
    url = demo_url % asin
    try:
        driver.get(url)
        text = driver.find_element_by_id('detailBullets_feature_div').text
        masin = re.findall('[A-Z0-9]{10}', text)[0]
        time.sleep(2)
        allList.append(masin)
        print(asin, masin, i)
        with open('masin.txt', 'a+') as f:
            f.write(masin + ',')
    except:
        pass
    finally:
        i += 1
