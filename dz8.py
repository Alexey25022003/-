# №1

import scrapy
from scrapy_splash import SplashRequest

class AvitoSpider(scrapy.Spider):
    name = 'avito'
    allowed_domains = ['avito.ru']

    def start_requests(self):
        # Запрос от пользователя
        query = "iPhone"

        url = f'https://www.avito.ru/moskva?q={query}' # Ссылка на результаты поиска
        yield SplashRequest(url, self.parse, args={'wait': 5})

    def parse(self, response):
        # Получение информации об объявлениях
        ads = response.xpath('//div[@data-marker="item"]')

        for ad in ads:
            # Извлечение данных из объявления
            title = ad.css('.iva-item-title::text').get()
            link = ad.css('.iva-item-title-link::attr(href)').get()
            price = ad.css('.price-text::text').get()
            description = ad.css('.iva-item-description::text').get()
            photo_container = ad.css('.gallery-img-wrapper')
            
            # Получение ссылки на большую фотографию
            large_photo_url = photo_container.css('.gallery-img-frame::attr(src)').get()
            
            # Получение ссылок на маленькие фотографии
            small_photos_urls = photo_container.css('.gallery-img-frame::attr(data-url)').getall()
            
            yield {
                'title': title,
                'link': link,
                'price': price,
                'description': description,
                'large_photo_url': large_photo_url,
                'small_photos_urls': small_photos_urls
            }

