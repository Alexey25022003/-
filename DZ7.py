#  1) Взять любую категорию товаров на сайте Касторама. Собрать следующие данные:
#  название;
#  все фото;
#  ссылка;
#  цена.

#Реализуйте очистку и преобразование данных с помощью ItemLoader. Цены должны быть в виде числового значения.# №1 
#Реализовать хранение скачиваемых файлов в отдельных папках, каждая из которых должна соответствовать 
#собираемому товару
            
import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, MapCompose
from scrapy.pipelines.files import FilesPipeline
import os

class CastoramaItem(scrapy.Item): # Создаем класс CastoramaItem
    title = scrapy.Field() # Создаем поле title, которое будет хранить название товара
    photos = scrapy.Field () # Создаем поле photos, которое будет хранить ссылки на фото товара
    link = scrapy.Field() # Создаем поле link, которое будет хранить ссылку на страницу товара
    price = scrapy.Field() # Создаем поле price, которое будет хранить цену товара

class CastoramaPipeline(FilesPipeline): # Создаем класс CastoramaPipelin который наследуется от FilesPipeline
    def file_path(self, request, response=None, info=None):  # Определяем метод filepath
        item = request.meta['item'] # Получаем объект item из запроса
        category_path = item['title'] #Название папки...
        file_name = os.path.basename(request.url) # Получаем имя файла из URL запроса
        return f'{category_path}/{file_name}' # Возвращаем путь сохранения файла

class CastoramaSpider(scrapy.Spider): # Создаем класс CastoramaSpider
    name = 'castorama'
    start_urls = ['https://www.castorama.ru/']

    custom_settings = { # Указываем, что результаты парсинга должны быть обработаны через CastoramaPipeline
        'ITEM_PIPELINES': {
            'project.pipelines.CastoramaPipeline': 1,
        }
    }

    def parse(self, response): # Будет вызываться для обработки стартовых URL-адресов.
        category_url = response.css('a[href*=instrumenty]::attr(href)').get() # Используем CSS для выбора ссылки на категорию товаров
        yield response.follow(category_url, callback=self.parse_category) # Используем response.follow, чтобы перейти по ссылке на категорию товаров и вызвать parse_category 

    def parse_category(self, response): # Будет вызываться для обработки страницы категории товаров
        for product in response.css('.b-teaser-product-list__product'): # Для каждого товара в категории
            loader = ItemLoader(item=CastoramaItem(), selector=product) # Создаем ItemLoader, связанный с объектом CastoramaItem

            # Используем TakeFirst, чтобы получить только первое значение
            loader.default_output_processor = TakeFirst()

            # Заполняем данные товара
            loader.add_css('title', '.b-teaser-product__title::text')
            loader.add_css('link', '.b-teaser-product__image a::attr(href)')
            loader.add_css('price', '.b-teaser-product__price::text', MapCompose(float))

            # Ссылки на все фото
            photos = product.css('.b-teaser-product__image img::attr(src)').getall() 
            # Передаем список фото для использования в pipeline
            loader.add_value('photos', photos) # Добавляем список фото в поле 'photos' класса ItemLoader

            yield loader.load_item()

    def file_downloaded(self, response, request, info, *, item=None): # Будет вызываться после скачивания файла
        return item

    def get_media_requests(self, item, info): # Будет вызываться для получения запросов на скачивание медиафайлов
        for photo_url in item['photos']:
            yield scrapy.Request(photo_url, meta={'item': item}) # Создаем scrapy.Request для скачивания фото

    def item_completed(self, results, item, info):  # Будет вызываться после завершения обработки объекта item.
        item.pop('photos', None) # Удаляем поле 'photos' из item, так как уже скачали все фото 
        return item # Возвращаем объект item без поля photos