from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from PCRAW import settings
from PCRAW.spiders.winestyle import WinestyleSpider
from PCRAW.spiders.amwine import AmwineSpider
from PCRAW.spiders.alcomarket import AlcomarketSpider

if __name__ == '__main__':
    args = dict()
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)
    process = CrawlerProcess(settings=crawler_settings)

    process.crawl(AlcomarketSpider)
    process.crawl(WinestyleSpider)
    process.crawl(AmwineSpider)
    process.start()
    process.start()
    process.start()
