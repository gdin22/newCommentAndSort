import smtplib
import xlwt
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from pymongo import MongoClient
import run
from collections import Counter

conn = MongoClient('localhost', 27017)
db = conn.amazon
comAndSort = db.comAndSort


# 发送邮件 密码写死
def smtp(msg_from, msg_to, subject, html_text, path, name):
    msg_from = msg_from
    passwd = 'stvqbfdfdydxhbff'
    msg_to = msg_to

    message = MIMEMultipart()
    message['From'] = Header(name, 'utf-8')
    message['To'] = Header("", 'utf-8')
    subject = subject
    message['Subject'] = Header(subject, 'utf-8')

    message.attach(MIMEText(html_text, 'plain', 'utf-8'))

    # 构造附件
    att1 = MIMEText(open(path, 'rb').read(), 'base64', 'utf-8')
    att1["Content-Type"] = 'application/octet-stream'
    # 这里的filename可以任意写，写什么名字，邮件中显示什么名字
    att1["Content-Disposition"] = 'attachment; filename="%s"' % path
    message.attach(att1)

    try:
        s = smtplib.SMTP_SSL("smtp.qq.com", 465)
        s.login(msg_from, passwd)
        s.sendmail(msg_from, msg_to, message.as_string())
        print('发送成功')
    except Exception as e:
        print('发送失败')
        print(e)
    finally:
        s.quit()


# 处理数据库 校对今昨两天的数据
# 返回各个星级的数量差 今昨的排行排行差 评论差 今天评论数
def make_message(asin):
    today_date = run.get_date_time()
    yes_date = run.get_date_time() - 24 * 60 * 60
    to_stars = comAndSort.find_one({'asin': asin, 'timestamp': today_date})['star']
    to_stars = Counter(to_stars)
    to_comment_num = comAndSort.find_one({'asin': asin, 'timestamp': today_date})['comment_num']
    yes_comment_num = comAndSort.find_one({'asin': asin, 'timestamp': yes_date})['comment_num']
    comment_up = to_comment_num - yes_comment_num
    star_level = ['5.0', '4.0', '3.0', '2.0', '1.0']
    each_stars = {}
    for star in star_level:
        each_stars[star] = to_stars[star]
    sort = {}
    sort['to_sort'] = comAndSort.find_one({'asin': asin, 'timestamp': today_date})['sort']
    sort['yes_sort'] = comAndSort.find_one({'asin': asin, 'timestamp': yes_date})['sort']
    sort['short_of'] = sort['to_sort'] - sort['yes_sort']
    return each_stars, sort, comment_up, to_comment_num


# 生成excel表格
def make_excel(asin_list):
    file, table = excel_head()
    all_list = []
    for asin in asin_list:
        try:
            each_stars, sort, comment_up, to_comment_num = make_message(asin)
            each_list = [asin, sort['to_sort'], sort['yes_sort'], sort['short_of'], to_comment_num, comment_up, each_stars['5.0'], each_stars['4.0'], each_stars['3.0'], each_stars['2.0'], each_stars['1.0']]
            all_list.append(each_list)
        except:
            pass
    path_name = str(run.get_date_time()) + '.xls'
    cols = len(all_list)
    rows = len(all_list[0])
    for i in range(cols):
        for j in range(rows):
            table.write(i + 1, j, all_list[i][j])
    file.save(path_name)
    return path_name


# 生成excel头
def excel_head():
    file = xlwt.Workbook()
    table = file.add_sheet('0')
    table.write(0, 0, 'asin')
    table.write(0, 1, '当日排名')
    table.write(0, 2, '昨日排名')
    table.write(0, 3, '排名对比')
    table.write(0, 4, '评论次数')
    table.write(0, 5, '评论数量提升')
    table.write(0, 6, '5.0 up')
    table.write(0, 7, '4.0 up')
    table.write(0, 8, '3.0 up')
    table.write(0, 9, '2.0 up')
    table.write(0, 10, '1.0 up')
    return file, table


if __name__ == "__main__":
    asin_list =['B0755BYDD9', 'B07K9GKRLV', 'B07646M8G4', 'B07FSF74ZF']
    file_path = make_excel(asin_list)
    # 发送部分
    msg_from = '1171341386@qq.com'
    msg_to = ['3139485269@qq.com']
    subject = 'asin stars sort'
    html_text = 'asin stars sort'
    path = file_path
    name = '王楚忠'
    smtp(msg_from, msg_to, subject, html_text, path, name)
