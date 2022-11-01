import os
import re
import sqlite3
from requests_html import HTMLSession
from datetime import datetime
from bs4 import BeautifulSoup

class Corbetts:
    def __init__(self):
        # TODO: add find product link
        self.find_product_id = re.compile(r'data-product-id="(\d*)"')
        self.find_product_name = re.compile(r'<a(.*?)>(.*?)</a>')
        self.find_pic_link = re.compile(r'<img(.*?)src="(.*?)"(.*?)>')
        self.find_original_price = re.compile(r'<span class="price price--rrp ng-binding">\$(.*?)</span>')
        self.find_sale_price = re.compile(r'<span class="price price--withoutTax price--main ng-binding">\$(.*?)</span>')
        self.find_product_link = re.compile(r'<a(.*?)href="(.*?)" ')

    def get_corbetts(self):
        burl = 'https://www.corbetts.com/categories/sale.html?page='
        datalist = self.get_data(burl)
        if not os.path.exists('.\\data\\'):
            os.makedirs('.\\data\\')
        dbpath = r'.\data\Corbetts_' + datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.db'
        if not os.path.exists(dbpath):
            self.initDB(dbpath)
            print('Database', dbpath, 'initialized')
        print('Saving data to database...')
        self.saveData2DB(dbpath, datalist)
        print('Completed, data saved to database', dbpath)

    def get_data(self, burl):
        datalist = []
        session = HTMLSession()
        # sometime response might be None, added try
        try:
            response = session.get(burl + '1')
        except Exception as e:
            response = session.get(burl + '1')
        response.html.render(timeout=15)
        html = response.html.html
        soup = BeautifulSoup(html, "html.parser")
        item_remain = int(soup.find('a', {'href': "https://www.corbetts.com/categories/sale.html#/filter:ss_on_sale:1:1"}).find('div', {'class': 'ng-binding'}).text[1:-1])

        page = 0
        sold_out = False
        while page < item_remain // 48 and not sold_out:  # 48 items each page
            page += 1
            print('Getting data from page', page)

            url = burl + str(page)
            session = HTMLSession()
            try:
                response = session.get(url)
            except Exception as e:
                response = session.get(url)
            response.html.render(timeout=15)
            html = response.html.html
            soup = BeautifulSoup(html, "html.parser")
            for item in soup.find_all('li', class_="ss-item product ng-scope"):

                name_a = str(item.find_all('a', {'class': 'ng-binding'})[0])
                sold_out_info = str(item.find_all('figure', {'class': 'card-figure'})[0])
                if 'Sold Out' in sold_out_info:
                    sold_out = True
                    break

                item = str(item)

                product_id = re.search(self.find_product_id, item).group(1)
                product_name = re.search(self.find_product_name, name_a).group(2)
                original_price = '0'
                original_price_raw = re.search(self.find_original_price, item)
                if original_price_raw:
                    original_price = original_price_raw.group(1).replace(',', '')
                sale_price = re.search(self.find_sale_price, item).group(1).replace(',', '')
                pic_link = re.search(self.find_pic_link, item).group(2)
                if original_price != '0':
                    discount_rate = str("{:.2f}".format(float(sale_price) / float(original_price)))
                else:
                    discount_rate = '0'
                product_link = re.search(self.find_product_link, item).group(2)
                datalist.append([product_id, product_name, original_price, sale_price, discount_rate, pic_link, product_link])
        return datalist


    def saveData2DB(self, dbpath, datalist):

        conn = sqlite3.connect(dbpath)
        cur = conn.cursor()

        for data in datalist:
            for index in range(len(data)):
                data[index] = '"' + data[index] + '"'
            sql = '''
            insert into sale_products (
                product_id, product_name, original_price, sale_price, discount_rate, pic_link, product_link
            )
            values (%s)''' % ",".join(data)
            cur.execute(sql)
            conn.commit()

        cur.close()
        conn.close()


    def initDB(self, dbpath):
        sql = '''
            create table sale_products
            (
                product_id integer primary key,
                product_name text,
                original_price real,
                sale_price real,
                discount_rate real,
                pic_link text,
                product_link text
            );
        '''
        conn = sqlite3.connect(dbpath)
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
        conn.close()
