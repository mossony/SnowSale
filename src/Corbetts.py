import re
import sqlite3
import urllib.error
import urllib.request
from requests_html import HTMLSession
from helpers import *

import xlwt
from bs4 import BeautifulSoup


def get_corbetts():
    burl = 'https://www.corbetts.com/categories/sale.html?page='

    print(getData(burl))
    pass

find_product_id = re.compile(r'data-product-id="(\d*)"')
find_product_name = re.compile(r'<a(.*?)>(.*?)</a>')
find_original_price = re.compile(r'<span class="price price--rrp ng-binding">\$(.*?)</span>')
find_sale_price = re.compile(r'<span class="price price--withoutTax price--main ng-binding">\$(.*?)</span>')


def getData(burl):
    datalist = []
    session = HTMLSession()
    response = session.get(burl+'1')
    response.html.render()
    html = response.html.html
    soup = BeautifulSoup(html, "html.parser")
    item_remain = int(soup.find('a', {'href': "https://www.corbetts.com/categories/sale.html#/filter:ss_on_sale:1:1"}).find('div', {'class':'ng-binding'}).text[1:-1])

    page = 1
    while page < item_remain // 48:  # 48 items each page
        item_remain -= 48
        url = burl + str(page)
        session = HTMLSession()
        response = session.get(url)
        response.html.render()
        html = response.html.html
        soup = BeautifulSoup(html, "html.parser")
        for item in soup.find_all('li', class_="ss-item product ng-scope"):
            data = []

            name_a = str(item.find_all('a', {'class':'ng-binding'})[0])
            item = str(item)

            product_id = re.search(find_product_id, item).group(1)
            product_name = re.search(find_product_name, name_a).group(2)
            original_price_raw = re.search(find_original_price, item)
            if original_price_raw:
                original_price = original_price_raw.group(1)
            sale_price = re.search(find_sale_price, item).group(1)

            print(product_id, product_name, sale_price, original_price)

            # link = re.findall(findLink, item)[0]
            # data.append(link)
            # imgLink = re.findall(findImgLink, item)[0]
            # data.append(imgLink)
            # titles = re.findall(findTitle, item)
            # if len(titles) == 2:
            #     ctitle = titles[0]
            #     data.append(ctitle)
            #     otitle = titles[1].replace("/", "")
            #     otitle = otitle.strip()
            #     data.append(otitle)
            # else:
            #     data.append(titles[0])
            #     data.append(' ')
            # rating = re.findall(findRating, item)[0]
            # data.append(rating)
            # ReviewNum = re.findall(findReviewNum, item)[0]
            # data.append(ReviewNum)
            # inq = re.findall(findInq, item)
            # if len(inq) != 0:
            #     inq = inq[0].replace("。", "")
            #     data.append(inq)
            # else:
            #     data.append("")
            # bd = re.findall(findBd, item)[0]
            # bd = re.sub('<br(\s+)?/>(\s+)?', " ", bd)
            # bd = re.sub('/', " ", bd)
            # data.append(bd.strip())
            #
            # datalist.append(data)

    save_path = "../Data"
    # saveData(save_path, datalist)
    return datalist