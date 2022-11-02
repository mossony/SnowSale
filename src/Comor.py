import os
import sqlite3
from requests_html import HTMLSession
from datetime import datetime
from bs4 import BeautifulSoup



class Comor:

    def get_comor(self):
        burl = 'https://comorsports.com/collections/sale?page={}&product_type=Snowboards,Snowboard+Boots,Snowboard+Bindings,Snow+Pants+%26+Bibs,Skis,Ski+Poles,Ski+Boots,Ski+Bindings'
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
            response = session.get(burl.format(1))
        except Exception as e:
            response = session.get(burl.format(1))
        response.html.render(timeout=15)
        html = response.html.html
        soup = BeautifulSoup(html, "html.parser")
        total_page = int(soup.find_all('span', {'class': "pagination__number"})[-1].find('a').text)

        page = 0
        while page < total_page:
            page += 1
            print('Getting data from page', page)
            url = burl.format(page)
            session = HTMLSession()
            try:
                response = session.get(url)
            except Exception as e:
                response = session.get(url)
            response.html.render(timeout=15)
            html = response.html.html
            soup = BeautifulSoup(html, "html.parser")

            for item in soup.find_all('div', {'class': 'product-block'}):
                product_name = item.find_all('div', {'class': 'product-block__title'})[0].text
                sale_price = item.find_all('div', {'class': 'product-price'})[0].find_all('span', {'class': ['money', 'product-price__item product-price__amount theme-money']})[0].text[1:].replace(',', '')
                original_price = '0'
                original_price_raw = item.find_all('span', {'class': 'product-price__item product-price__compare theme-money'})
                if original_price_raw:
                    original_price = original_price_raw[0].text[1:].replace(',', '')
                if original_price != '0':
                    discount_rate = str("{:.2f}".format(float(sale_price) / float(original_price)))
                else:
                    discount_rate = '0'

                product_id = item['data-product-id']
                product_link = 'https://comorsports.com/' + item.find_all('a', {'class': 'product-link'})[0]['href']

                pic_img = item.find_all('img')[0]

                pic_link = pic_img['data-src'].replace(f'{{width}}x', '1024x1024')
                if '180w' in pic_link:
                    pic_link = pic_link[:pic_link.index('180w')]

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
            insert or ignore into sale_products (
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
