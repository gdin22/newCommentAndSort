from comAndSort import ComAndSort
import time
import smtp
import datetime
from pymongo import MongoClient
from realAsin import realAsin
conn = MongoClient('localhost', 27017)
db = conn.amazon
comAndSort = db.comAndSort


# 获取每天的时间戳 以"天"为最小单位
def get_date_time():
    date_style = '%Y.%m.%d'
    date_string = time.strftime(date_style, time.localtime(time.time()))
    timeArrary = time.strptime(date_string, date_style)
    time_stamp = int(time.mktime(timeArrary))
    return time_stamp


# 通过asin 和 时间戳 返回评论数还有排行
def get_sql(asin, timestamp):
    try:
        dict = comAndSort.find_one({'asin': asin, 'timestamp': timestamp})
        comment_num = dict.get('comment_num', 0)
        sort = dict.get('sort', 0)
        return comment_num, sort
    except:
        return 0, 0


def test():
    asin = 'B0755BYDD9'
    demo_url = 'https://www.amazon.com/dp/%s'
    cms = ComAndSort()
    url = demo_url % asin
    int_sort_num, comment_num = cms.get_comment_num_sort(url)
    print(int_sort_num, comment_num)


if __name__ == '__main__':
    while True:
        start_time = time.time()
        date_time = get_date_time()
        yes_time = date_time - 24 * 60 * 60

        # 父asin的list 可以修改
        asin_list = realAsin
        demo_url = 'https://www.amazon.com/dp/%s'
        for asin in asin_list:
            print(asin)
            time.sleep(2)
            cms = ComAndSort()
            url = demo_url % asin
            try:
                try:
                    int_sort_num, comment_num = cms.get_comment_num_sort(url)
                except:
                    int_sort_num, comment_num = cms.get_comment_num_sort(url)

                try:
                    yes_comment_num, yes_sort = get_sql(asin, yes_time)
                    comment_up_num = comment_num - yes_comment_num
                except:
                    comment_up_num = 0
                if comment_up_num != 0:
                    to_comment = cms.get_sort_comment(asin, comment_up_num)
                else:
                    to_comment = {}
                    to_comment['size'] = []
                    to_comment['star'] = []
                    to_comment['color'] = []
                comAndSort.insert_one({'asin': asin, 'timestamp': date_time, 'color': to_comment.get('color'),
                                       'size': to_comment.get('size'), 'star': to_comment.get('star'),
                                       'comment_num': comment_num, 'sort': int_sort_num})
            except:
                pass

        # 发送部分
        today = datetime.datetime.now()
        today_string = '%s年%s月%s日' % (today.year, today.month, today.day)
        file_path = smtp.make_excel(asin_list)
        msg_from = '1171341386@qq.com'
        msg_to = ['3139485269@qq.com']  # 接受邮件的邮箱
        subject = '%s评论排行报表' % today_string
        html_text = '%s评论排行报表' % today_string
        path = file_path
        name = '王楚忠'
        smtp.smtp(msg_from, msg_to, subject, html_text, path, name)

        end_time = time.time()
        until_time = end_time - start_time
        print(until_time)
        time.sleep(24 * 60 * 60 - until_time)
