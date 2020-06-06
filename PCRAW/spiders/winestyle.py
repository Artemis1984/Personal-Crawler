# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from pprint import pprint


class WinestyleSpider(scrapy.Spider):
    name = 'winestyle'
    allowed_domains = ['winestyle.ru']
    start_urls = ['https://winestyle.ru/']

    def __init__(self):
        super(WinestyleSpider, self).__init__()
        self.sections = ['wine', 'champagnes-and-sparkling', 'whisky', 'cognac', 'beer', 'liqueur', 'vodka', 'rum']
        self.section = self.sections[0]
        self.page = '0'
        self.url = 'https://winestyle.ru/'
        self.start_urls = ['https://winestyle.ru/' + self.section + '/all/?page=' + str(int(self.page) + 1)]

    def parse(self, response: HtmlResponse):

        if len(response.xpath("//form[@class= 'item-block ' and .//div[@class= 'stock  has-hover stock-dot']]")) == 0:
            self.change_section()

        self.page = str(int(self.page) + 1)
        page_link = self.url + self.section + '/all/?page=' + self.page
        yield response.follow(page_link, callback=self.parse)

        product_names = response.xpath(
            "//form[@class= 'item-block ' and .//div[@class= 'stock  has-hover stock-dot']]//p[@class= 'title']//text()").extract()
        product_prices = response.xpath(
            "//form[@class= 'item-block ' and .//div[@class= 'stock  has-hover stock-dot']]//div[@class= 'price ']/text()").extract()
        product_links = response.xpath(
            "//form[@class= 'item-block ' and .//div[@class= 'stock  has-hover stock-dot']]//p[@class= 'title']//@href").extract()
        product_emages = response.xpath(
            "//form[@class= 'item-block ' and .//div[@class= 'stock  has-hover stock-dot']]//noscript").extract()

        product_features = response.xpath(
            "//form[@class= 'item-block ' and .//div[@class= 'stock  has-hover stock-dot']]//ul[@class= 'list-description']//text()").extract()

        list_ = ['']
        for i in product_features:
            if ':' in i:
                list_.append(i)
            elif ',' in i:
                list_[-1] += i + ' '

            else:
                list_[-1] += i

        for i in range(len(list_)):
            list_[i] = list_[i].replace('\n', '')

        del list_[0]

        indexes = []
        for i in range(len(list_)):
            if 'Регион:' in list_[i]:
                indexes.append(i)

        product_features = []

        for i in range(len(indexes) - 1):
            product_features.append(list_[indexes[i]:indexes[i + 1]])
            if i == len(indexes) - 2:
                product_features.append(list_[indexes[i + 1]:])

        feature_list = []
        for i in product_features:
            my_dict = dict()
            for j in i:
                my_dict[j[:j.index(':')]] = j[j.index(':') + 1:].replace('\t', '')

            feature_list.append(my_dict)

        product_list = []

        for name, price, link, image, feature in zip(product_names, product_prices, product_links, product_emages,
                                                     feature_list):
            product_dict = dict()
            product_dict['name'] = name.replace('\"', '')
            product_dict['price'] = price.replace(' ', '')
            product_dict['link'] = 'https://winestyle.ru' + link
            product_dict['image'] = image[image.index('src=') + 5:image.index('"></noscript>')]
            product_dict['features'] = feature

            pprint(product_dict)
            product_list.append(product_dict)

            print('=' * 50)

    def change_section(self):

        if self.section == self.sections[-1]:
            self.section = self.sections[0]
        else:
            self.section = self.sections[self.sections.index(self.section) + 1]

        self.page = '0'
