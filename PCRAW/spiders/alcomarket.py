# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from pprint import pprint
import re


class AlcomarketSpider(scrapy.Spider):
    name = 'alcomarket'
    allowed_domains = ['alcomarket.ru']
    start_urls = ['https://alcomarket.ru/catalog/wine/?PAGEN_1=1']

    def __init__(self):
        super(AlcomarketSpider, self).__init__()
        self.sections = ['wine', 'shampanskoe-i-igristoe', 'krepkiy-alkogol']
        self.section = self.sections[0]
        self.url = f'https://amwine.ru/catalog/{self.section}/?PAGEN_1=1'
        self.product_list = list()

    def parse(self, response: HtmlResponse):

        product_links = response.xpath(
            "//a[@class= 'catalog_item_href' and ..//div[@class= 'catalog_item_buy']]/@href").extract()

        for i in product_links:
            link = 'https://alcomarket.ru' + i
            yield response.follow(link, callback=self.get_product_info)

        next_page = response.xpath("//a[@title= 'Следующая страница']/@href").extract_first()
        if next_page and len(product_links) != 0:
            yield response.follow('https://alcomarket.ru' + next_page, callback=self.parse)
        else:
            self.change_section()
            yield response.follow(self.url, callback=self.parse)

    def get_product_info(self, response: HtmlResponse):

        product_dict = dict()

        product_dict['name'] = response.xpath("//div[@class= 'h1 hidden-xs']/text()").extract_first()
        product_dict['price'] = response.xpath("//div[@class= 'price']/span/text()").extract_first()
        product_dict['image'] = 'https://alcomarket.ru' + response.xpath(
            "//div[@class= 'img_block']/img/@data-src").extract_first()
        product_dict['link'] = response.url

        feature_values = response.xpath("//div[@class= 'col-xs-6 col-sm-3']//text()").extract()
        feature_titles = response.xpath("//div[@class= 'info_title_s']/text()").extract()

        list_ = list()
        for i in feature_values:
            for j in i:
                if not j.isspace():
                    list_.append(i.replace('\n', '').replace('\t', ''))
                    break

        my_dict = {}

        title = None
        for j in list_:
            if j in feature_titles:
                title = j
                my_dict[title] = ''
                continue
            else:
                my_dict[title] += j + ', '

        for key, value in zip(my_dict.keys(), my_dict.values()):
            if len(re.findall(', ', value)) == 1:
                my_dict[key] = value.replace(', ', '')

        my_dict['Страна'] = my_dict['Страна'][1:]

        product_dict['features'] = my_dict

        self.product_list.append(product_dict)
        pprint(product_dict)
        print('=' * 30)

    def change_section(self):
        if self.section == self.sections[-1]:
            self.section = self.sections[0]
        else:
            self.section = self.sections[self.sections.index(self.section) + 1]

        self.url = f'https://alcomarket.ru/catalog/{self.section}/?PAGEN_1=1'
