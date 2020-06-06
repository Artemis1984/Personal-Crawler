# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from selenium import webdriver
import time
from pprint import pprint
import collections


class AmwineSpider(scrapy.Spider):
    name = 'amwine'
    allowed_domains = ['amwine.ru']
    start_urls = ['https://amwine.ru/']

    def __init__(self):
        super(AmwineSpider, self).__init__()
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        self.driver = webdriver.Chrome("/Users/artemtarassov/PycharmProjects/Personal-Crawler/chromedriver",
                                       options=options)
        self.sections = ['vino', 'igristoe_vino_i_shampanskoe', 'krepkie_napitki/', 'pivo']
        self.section = self.sections[0]
        self.url = f'https://amwine.ru/catalog/{self.section}/?page='
        self.page = '0'
        self.product_list = list()

    def parse(self, response: HtmlResponse):

        while True:
            self.page = str(int(self.page) + 1)
            page_link = self.url + self.page

            self.driver.get(page_link)
            try:
                self.driver.find_element_by_xpath("//div[@class= 'confirmation-popup__btn']").click()
            except:
                pass

            product_links = self.driver.find_elements_by_xpath(
                "//div[@class= 'catalog-section-itemlist parent-selector js-catalog-section-items']//div[@class= 'catalog-list-item__container' and .//div[@class= 'bth-add-to-cart-block js-add-to-cart-wrapper']]/a")

            if len(product_links) == 0:
                self.change_section()
                continue

            for link in product_links:
                yield response.follow(link.get_attribute('href'), callback=self.get_product_info)

    def get_product_info(self, response: HtmlResponse):

        product_dict = dict()
        product_dict['name'] = response.xpath('//h1/text()').extract_first().replace('\n', '').replace(' ' * 28,
                                                                                                       '').replace(
            ' ' * 24, '')
        product_dict['price'] = response.xpath("//span[@itemprop= 'price']/text()").extract_first()
        product_dict['link'] = response.url
        product_dict['image'] = 'https://www.amwine.ru' + response.xpath(
            "//div[@class = 'catalog-element-info__picture']/img/@src").extract_first()

        product_features_titles = response.xpath("//span[@class= 'about-wine__param-title']").extract()
        product_features_values = response.xpath("//span[@class= 'about-wine__param-value']//text()").extract()

        print(response.url)

        for i in range(len(product_features_values)):
            product_features_values[i] = product_features_values[i].replace('\n', '').replace(' ' * 60, '').replace(
                ' ' * 28, '').replace(' ' * 32, '').replace(' ' * 4, '')

        feature_values = []
        for i in product_features_values:
            if i != '':
                feature_values.append(i)

        for i in range(len(product_features_titles)):
            product_features_titles[i] = product_features_titles[i].replace('\n', '').replace(' ' * 16, '')[
                                         product_features_titles[i].index('\">') + 2:]
            product_features_titles[i] = product_features_titles[i][:product_features_titles[i].index('</span>')]

        my_dict = dict()

        for title, value in zip(product_features_titles, feature_values):
            my_dict[title] = value

        product_dict['features'] = my_dict

        pprint(product_dict)

        self.product_list.append(product_dict)

        print('=' * 50)

    def change_section(self):
        if self.section == self.sections[-1]:
            self.section = self.sections[0]
        else:
            self.section = self.sections[self.sections.index(self.section) + 1]
        self.page = '0'
        self.url = f'https://amwine.ru/catalog/{self.section}/?page='
