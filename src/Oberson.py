import ast
import os
import re
import sqlite3
from time import sleep

from requests_html import HTMLSession
from datetime import datetime
from bs4 import BeautifulSoup
import math
from selenium import webdriver
import webbrowser

from selenium.webdriver.common.by import By


class Oberson:
    def __init__(self):
        self.find_product_id = re.compile(r'data-product-id="(\d*)"')
        # self.find_product_name = re.compile(r'<a(.*?)>(.*?)</a>')
        self.find_pic_link = re.compile(r'<img(.*?)src="(.*?)"')
        self.find_original_price = re.compile(
            r'<span class="product-price__item product-price__compare theme-money">\$(.*?)<')
        self.find_sale_price = re.compile(
            r'<span(.*?)product-price__amount(.*?)\$(.*?)<')
        self.find_product_link = re.compile(r'<a(.*?)(product-link)?href="(.*?)"(product-link)?')
        self.find_item_info = re.compile(r'<script type="application/ld\+json">(.*?)</script>')

    def get_oberson(self):
        snowboard_burl = 'https://www.oberson.com/en/snowboard?discount_percent%5Bfilter%5D=25%2C10934&discount_percent%5Bfilter%5D=30%2C5760&discount_percent%5Bfilter%5D=20%2C5759&discount_percent%5Bfilter%5D=40%2C5761&discount_percent%5Bfilter%5D=15%2C10933'
        ski_burl = 'https://www.oberson.com/en/alpine-skis?discount_percent%5Bfilter%5D=25%2C10934&discount_percent%5Bfilter%5D=40%2C5761&discount_percent%5Bfilter%5D=30%2C5760&discount_percent%5Bfilter%5D=20%2C5759&discount_percent%5Bfilter%5D=15%2C10933&discount_percent%5Bfilter%5D=35%2C10935'
        datalist = self.get_data(snowboard_burl)
        datalist.extend(self.get_data(ski_burl))
        if not os.path.exists('.\\data\\'):
            os.makedirs('.\\data\\')
        dbpath = r'.\data\Oberson_' + datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.db'
        if not os.path.exists(dbpath):
            self.initDB(dbpath)
            print('Database', dbpath, 'initialized')
        print('Saving data to database...')
        self.saveData2DB(dbpath, datalist)
        print('Completed, data saved to database', dbpath)

    def get_data(self, burl):
        datalist = []
        driver = webdriver.Chrome()
        driver.get(burl)
        # sometime response might be None, added try

        sleep(5)
        # driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        reach_end = False
        while not reach_end:
            try:
                load_button = driver.find_element(By.XPATH, '//*[@id="plp_article"]/div/div[2]/div[3]/div[1]/div/button')
                load_button.click()
                sleep(2)
            except:
                reach_end = True
        print('reach end')
        html = driver.page_source
        # soup = BeautifulSoup(html, "html.parser")
        # for item in soup.find_all('div', {'class': 'itemConfigurable-root-1s1'}):
        items = re.findall(self.find_item_info, html)
        for item in items:
            item = ast.literal_eval(item)
            product_id = item['sku']
            product_name = item['name']
            original_price = item['offers'].get('highPrice', 1)
            original_price = str(original_price)
            sale_price = item['offers'].get('lowPrice', 1)
            if sale_price == 1:
                sale_price = item['offers'].get('price', 1)
            sale_price = str(sale_price)
            if original_price != '1':
                discount_rate = str("{:.2f}".format(float(sale_price) / float(original_price)))
            else:
                discount_rate = '0'
            pic_link = item['image'][0]
            product_link = item['offers']['url']

            datalist.append([product_id, product_name, original_price, sale_price, discount_rate, pic_link, product_link])

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
                product_id text primary key,
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
