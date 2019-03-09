import re
import scrapy


class UndercoverResearchItem(scrapy.Item):
    # define the fields for your item here like:
    Link = scrapy.Field()


class UnderCoverResearchSpider(scrapy.Spider):

    name = 'undercoverresearch'
    allowed_domains = ["undercoverresearch.net"]

    start_urls = ['https://undercoverresearch.net']
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) '
                             'AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/41.0.2228.0 Safari/537.36', }

    available_links = []

    parse_result_count = 0

    def __init__(self, *args, **kwargs):
        super(UnderCoverResearchSpider, self).__init__(site_name=self.allowed_domains[0], *args, **kwargs)
        self.current_page = 0

    def start_requests(self):
        yield scrapy.Request(url=self.start_urls[0], callback=self.parse_main_pages, headers=self.headers)

    def parse_main_pages(self, response):
        menu_links = list(set(response.xpath('//a/@href').extract()))

        if len(menu_links) > 0:
            for link in menu_links:
                if 'http' in link:
                    self.available_links.append(link)

                if 'undercoverresearch.net' in link:
                    yield scrapy.Request(url=link, callback=self.parse_first_step, dont_filter=True)

    def parse_first_step(self, response):
        links = list(set(response.xpath('//a/@href').extract()))
        for link in links:
            if 'http' in link:
                self.available_links.append(link)

            if 'undercoverresearch.net' in link:
                yield scrapy.Request(url=link, callback=self.parse_page, dont_filter=True)

    def parse_page(self, response):
        result = UndercoverResearchItem()

        page_links = []

        links = list(set(response.xpath('//a/@href').extract()))
        if len(links) > 0:
            for link in links:
                if 'http' in link:
                    if self.parse_result_count == 0:
                        self.available_links.append(link)
                    else:
                        page_links.append(link)

        if self.parse_result_count == 0:
            links = list(set(self.available_links))
            self.parse_result_count += 1
            for link in links:
                result['Link'] = link
                yield result

        else:
            for p_link in page_links:
                result['Link'] = p_link
                yield result

    @staticmethod
    def _clean_text(text):
        text = text.replace("\n", " ").replace("\t", " ").replace("\r", " ")
        text = re.sub("&nbsp;", " ", text).strip()

        return re.sub(r'\s+', ' ', text)