import os
import re
import sqlite3
from requests_html import HTMLSession
from datetime import datetime
from bs4 import BeautifulSoup


class Rudeboys:
    def __init__(self):
        self.find_product_id = re.compile(r'data-product-id="(\d*)"')
        # self.find_product_name = re.compile(r'<a(.*?)>(.*?)</a>')
        self.find_pic_link = re.compile(r'<img(.*?)src="(.*?)"')
        self.find_original_price = re.compile(
            r'<span class="product-price__item product-price__compare theme-money">\$(.*?)<')
        self.find_sale_price = re.compile(
            r'<span(.*?)product-price__amount(.*?)\$(.*?)<')
        self.find_product_link = re.compile(r'<a(.*?)(product-link)?href="(.*?)"(product-link)?')

    def get_rudeboys(self):
        burl = 'https://rudeboys.com/collections/sale-bindings?page='
        datalist = self.get_data(burl)
        if not os.path.exists('.\\data\\'):
            os.makedirs('.\\data\\')
        dbpath = r'.\data\Rudeboys_' + datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.db'
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
        item_remain = int(soup.find('div', {'class': "utility-bar__centre"}).text[:2])

        page = 0
        while page < item_remain // 24:  # 48 items each page
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

            for item in soup.find('div', {'class': 'filters-adjacent collection-listing'}).find_all('div', {
                'class': ['product-block cc-animate-init -in cc-animate-complete', 'product-block cc-animate-init']}):
                name_div = item.find_all('div', {'class': 'product-block__title'})[0]
                item = str(item)

                product_id = re.search(self.find_product_id, item).group(1)
                product_name = name_div.text
                original_price = '0'
                original_price_raw = re.search(self.find_original_price, item)
                if original_price_raw:
                    original_price = original_price_raw.group(1).replace(',', '')
                sale_price = re.search(self.find_sale_price, item).group(3).replace(',', '')
                pic_link = re.search(self.find_pic_link, item).group(2)
                pic_link = pic_link.replace(f'{{width}}x', '1024x1024')
                if original_price != '0':
                    discount_rate = str("{:.2f}".format(float(sale_price) / float(original_price)))
                else:
                    discount_rate = '0'
                product_link = re.search(self.find_product_link, item).group(3)
                product_link = 'https://rudeboys.com/' + product_link
                print([product_id, product_name, original_price, sale_price, discount_rate, pic_link, product_link])
                datalist.append(
                    [product_id, product_name, original_price, sale_price, discount_rate, pic_link, product_link])
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
