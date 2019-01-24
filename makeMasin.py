from pymongo import MongoClient
from asin2Masin import Asin2asin
import time
conn = MongoClient('localhost', 27017)
db = conn.followsell

if __name__ == "__main__":
    asinDict = db.asin.find_one()['asin']
    asinList = list(asinDict.keys())
    to = Asin2asin()
    masinList = []
    # print(asinList)
    for asin in asinList:
        masin = to.getMasin(asin)
        masinList.append(masin)
        time.sleep(2)
        print('%s %s' % (asin, masin))
        with open('masin.txt', 'a+') as f:
            f.write(masin + ' ')
    print(masinList)
