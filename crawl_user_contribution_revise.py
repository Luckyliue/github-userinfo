import csv
import requests
from lxml import html
import time
from datetime import datetime, timedelta
# import pandas as pd
import os
import random
import sys

header = {
     # 'User-Agent': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Maxthon 2.0)',
     # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36',
     # 'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.94 Safari/537.36',
     # 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36'
     # 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.11 (KHTML, like Gecko) Ubuntu/11.10 Chromium/27.0.1453.93 Chrome/27.0.1453.93 Safari/537.36'
     # 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:21.0) Gecko/20100101 Firefox/21.0'
     # 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:21.0) Gecko/20130331 Firefox/21.0'
     # 'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:21.0) Gecko/20100101 Firefox/21.0'
     # 'Connection': 'keep-alive',
     # 'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
     # 'Host': 'github.com',
     # 'Accept': 'application/json'
}
ua_list = ['Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Maxthon 2.0)',
           'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36',
           'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.94 Safari/537.36',
           'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36',
           'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.11 (KHTML, like Gecko) Ubuntu/11.10 Chromium/27.0.1453.93 Chrome/27.0.1453.93 Safari/537.36',
           'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:21.0) Gecko/20100101 Firefox/21.0',
           'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:21.0) Gecko/20130331 Firefox/21.0',
           'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:21.0) Gecko/20100101 Firefox/21.0']

def shijian(start, end):
    begin_date = datetime.strptime(start, '%Y-%m-%d')
    end_date = datetime.strptime(end, '%Y-%m-%d')
    datelist = []
    while begin_date <= end_date:
        begin_str = begin_date.strftime("%Y-%m-%d")
        datelist.append(begin_str)
        begin_date += timedelta(days=1)
    return datelist

def write_csv(filename, line):
    with open(filename, 'a', newline='', encoding='utf-8') as csvf:
        writer = csv.writer(csvf, dialect='excel')
        writer.writerow(line)

def crawl(id, html_url, date_from, date_to, year_start, year_end):
    datelst = shijian(year_start, year_end)
    date_con = {d: 0 for d in datelst}
    count = 0
    while True:
        count += 1
        tag_url = '{}?tab=overview&from={}&to={}'.format(html_url, date_from, date_to)
        try:
            time.sleep(0.1)
            page = requests.get(tag_url, headers={'User-Agent': '%s' % random.choice(ua_list)})
            if page.status_code != 200 and page.status_code != 404:
                print("Error, sleep 5 seconds")
                print(page.status_code)
                print(tag_url)
                time.sleep(5)
            elif page.status_code == 404:
                return False
            else:
                try:
                    tree = html.fromstring(page.text)
                    all = tree.xpath('//*[@class="border py-2 graph-before-activity-overview"]/div/svg/g/g')
                    for g in all:
                        for rect in g:
                            count = rect.xpath('@data-count')[0]
                            date = rect.xpath('@data-date')[0]
                            if year_start <= date <= year_end:
                                date_con[date] = count
                    break
                except Exception as e1:
                    print(e1)
                    time.sleep(1)
        except Exception as e:
            print(e, 'sleep 5 seconds')
            time.sleep(5)
        if count > 10:  # 请求10次不成功
            with open('error.txt', 'a') as tf:
                tf.write(year_start+'\t'+id+'\t'+html_url+'\n')
            return False
    return list(date_con.values())


def main(year, startdate, enddate):
    # if year == 2008:
    #     date_oneyear = shijian('%s-02-27' % year, '%s-12-31' % year)
    # else:
    date_oneyear = shijian('{}-{}'.format(year,startdate), '{}-{}'.format(year,enddate))
    for date in date_oneyear:
        datelist = shijian(date, '2020-11-10')
        # df = pd.DataFrame(columns=datelist)
        done_id = []
        if os.path.exists('contribution/%s.csv' % date):
            with open('contribution/%s.csv' % date, 'r', encoding='utf-8') as f1:
                reader = csv.reader(f1)
                for row in reader:
                    done_id.append(row[0])
        else:
            write_csv('contribution/%s.csv' % date, ['']+datelist)
        with open('{}/{}.csv'.format(year, date), 'r', encoding='utf-8') as csvf:
            reader = csv.reader(csvf)
            for row in reader:
                if row[6] == 'html_url':
                    continue
                skip = False
                id = row[1]
                if id not in done_id:
                    html = row[6]
                    con_list = []
                    for y in range(int(year), 2021):
                        if y == year:
                            contribu = crawl(id, html, '%s-12-01'%y, '%s-12-31'%y, date, '%s-12-31'%y)
                        elif y == 2020:
                            contribu = crawl(id, html, '2020-11-01', '2020-11-11', '2020-01-01', '2020-11-10')
                        else:
                            contribu = crawl(id, html, '%s-12-01'%y, '%s-12-31'%y, '%s-01-01'%y, '%s-12-31'%y)

                        if contribu is False:
                            skip = True
                            break
                        else:
                            con_list += contribu
                    if skip is False:
                        # df.loc[id] = con_list
                        write_csv('contribution/%s.csv' % date, [id] + con_list)
                    else:
                        continue
                    print(id)
        # df.to_csv('contribution/%s.csv' % date)
        print(date)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3])
