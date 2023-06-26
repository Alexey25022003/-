# Написать программу, которая собирает входящие письма из своего или тестового почтового ящика
# и сложить данные о письмах в базу данных (от кого, дата отправки, тема письма, текст письма полный)
# Логин тестового ящика: study.ai_172@mail.ru
# Пароль тестового ящика: Ferrum123!

import time
from pprint import pprint
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from pymongo import MongoClient


def write_to_database(mail): # Функция сохранения данных о письме в базу данных.
    client = MongoClient('127.0.0.1', 27017) # Подключаемся к MongoDB
    db = client['mail_db'] # Выбираем базу данных с названием 'mail_db'
    mail_data = db.mail # Выбираем 'mail' в базе данных
    if mail_data.find_one({'link': mail['link']}): # Проверяем, есть ли уже письмо с такой же ссылкой в базе данных
        print(f'Duplicated mail {mail["link"]}')
    else:
        mail_data.insert_one(mail)
        print(f'Success insert the link {mail["link"]}') # Вставляем данные о письме в коллекцию 'mail'


url = 'https://e.mail.ru'
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36'}
options = Options() # Создаем объект настроек для браузера Chrome
options.add_argument('start-maximized') # Устанавливаем максимальный размер окна браузера

s = Service('./chromedriver') # Создаем сервис для запуска драйвера Chrome
driver = webdriver.Chrome(service=s, options=options) # Создаем экземпляр драйвера Chrome с настройками и сервисом

driver.get('https://account.mail.ru/login') # Открываем страницу
button = driver.find_element(By.XPATH, '//div[contains(@class, "box-0-2-119")]') # Нажимаем на кнопку почта
button.click()

elem = driver.find_element(By.XPATH, '//input[@name="username"]') # Находим элемент ввода логина по XPath, вводим данные
elem.send_keys('study.ai_172@mail.ru')
elem.send_keys(Keys.ENTER)
elem = driver.find_element(By.XPATH, '//input[@name="password"]') # Находим элемент ввода пароля по XPath, вводим данные
elem.send_keys('Ferrum123!')
elem.send_keys(Keys.ENTER)

wait = WebDriverWait(driver, 30) 
elem = wait.until(EC.element_to_be_clickable((By.XPATH, '//a[contains(@class, "llc ")]'))) # Ждем пока появится первое письмо
links_set = set()
last_link = ''
while True:
    links = driver.find_elements(By.XPATH, '//a[contains(@class, "llc ")]') # Находим все элементы с ссылками на письма
    if last_link == links[-1].get_attribute('href'): # Если последний найденный элемент совпал с предыдущим, значит мы дошли до конца списка писем
        break 
    else:
        last_link = links[-1].get_attribute('href')
    actions = ActionChains(driver)
    for el in links: # Добавляем новые ссылки на письма в linksset, чтобы небыло дублирования
        links_set.add(el.get_attribute('href'))
    actions.move_to_element(links[-1])
    actions.perform()

mail_list = []
for link in list(links_set): # Для каждой ссылки на письмо получаем данные о нем с помощью Selenium
    mail_data = {} 
    driver.get(link)
    driver.implicitly_wait(35)
    title = driver.find_element(By.TAG_NAME, 'h2').text # Находим заголовок письма, имя и email отправителя, дату отправки и текст письма
    sender_info = driver.find_element(By.XPATH, '//div[@class="letter__author"]')
    author_name = sender_info.find_element(By.XPATH, './span[@class="letter-contact"]').text
    author_email = sender_info.find_element(By.XPATH, './span[@class="letter-contact"]').get_attribute('title')
    date = sender_info.find_element(By.XPATH, './div[@class="letter__date"]').text
    body = driver.find_element(By.XPATH, "//div[@class='letter-body']").text
    mail_data['link'] = link # Заполняем данными о письме
    mail_data['author_name'] = author_name
    mail_data['author_email'] = author_email
    mail_data['title'] = title
    mail_data['letter_date'] = date
    mail_data['letter_body'] = body
    print(mail_data['title'])
    write_to_database(mail_data) # Пишем данные о письме в MongoDB
    mail_list.append(mail_data)

pprint(mail_list)
