#Необходимо собрать информацию о вакансиях на вводимую должность (используем input или через аргументы получаем должность) с сайта HH. Приложение должно #анализировать все страницы сайта. Получившийся список должен содержать в себе минимум:
#Наименование вакансии.
#Предлагаемую зарплату (разносим в три поля: минимальная и максимальная и валюта. цифры преобразуем к цифрам).
#Ссылку на саму вакансию.
#Сайт, откуда собрана вакансия.

import json # импортируем модуль для работы с форматом JSON
from bs4 import BeautifulSoup as bs  # импортируем функцию BeautifulSoup из модуля bs4 для работы с HTML
import requests # импортируем модуль для отправки HTTP-запросов

base_url ='https://www.hh.ru/vacancies' # переменной base_url присваиваем URL сайта hh.ru с вакансиями

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36'}  # переменной headers присваиваем словарь с заголовком User-Agent,

keyword = input('Введите вакансию: ')

url = f'{base_url}/{keyword}' # формируем URL адрес вакансии, добавляя к базовому URL текст из переменной keyword
response = requests.get(url, headers=headers) # отправляем GET-запрос на URL, передавая заголовки headers
dom = bs(response.text, 'html.parser') # парсим HTML-контент страницы в объект BeautifulSoup
vacancies = dom.find_all('div', {'class': 'vacancy-serp-item'}) # выбираем все элементы div с классом vacancy-serp-item из HTML-контента страницы и сохраняем их в переменную vacancies как список элементов.

# Перебор страниц 
def max_num():
    maxnumm = 0
    for item in dom.find_all('a', {'data-qa': 'pager-page'}):
        maxnumm = list(item.strings)[0].split(" ")[-1]
    return maxnumm

max_page = int(max_num())

# Cбор данных
def data_collect(pages):
    vacancies_list = []
    for page in range(pages):
        url2 = f'{base_url}/{keyword}?page={page}'
        response2 = requests.get(url2, headers=headers)
        dom2 = bs(response2.text, 'html.parser')
        vacancies2 = dom2.find_all('div', {'class': 'vacancy-serp-item'})
        for vacancy in vacancies2:
            vacancy_data = {}
            vacancy_title = vacancy.find('a', {'data-qa': 'vacancy-serp__vacancy-title'}).text.strip()
            vacancy_employer = vacancy.find('div', {'class': 'vacancy-serp-item__meta-info-company'}).text.strip()
            vacancy_link = vacancy.find('a', {'data-qa': 'vacancy-serp__vacancy-title'}).get('href')
            vacancy_salary = vacancy.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'})
            vacancy_salary_data = {'min_salary': '', 'max_salary': '', 'currency': ''}
            if vacancy_salary is None:
                vacancy_salary_data['min_salary'] = 'None'
                vacancy_salary_data['max_salary'] = 'None'
                vacancy_salary_data['currency'] = 'None'
            else:
                vacancy_salary = vacancy_salary.text.replace("\u202f", '').split()
                if 'от' in vacancy_salary:
                    if 'руб.' in vacancy_salary:
                        vacancy_salary_data['min_salary'] = int(vacancy_salary[1])
                        vacancy_salary_data['max_salary'] = 'None'
                        vacancy_salary_data['currency'] = 'руб.'
                if 'до' in vacancy_salary:
                    if 'руб.' in vacancy_salary:
                        vacancy_salary_data['min_salary'] = 'None'
                        vacancy_salary_data['max_salary'] = int(vacancy_salary[1])
                        vacancy_salary_data['currency'] = 'руб.'
                if 'от' not in vacancy_salary and 'до' not in vacancy_salary:
                    if 'руб.' in vacancy_salary:
                        vacancy_salary_data['min_salary'] = int(vacancy_salary[0])
                        vacancy_salary_data['max_salary'] = int(vacancy_salary[2])
                        vacancy_salary_data['currency'] = 'руб.'
            vacancy_data['vacancy_title'] = vacancy_title
            vacancy_data['vacancy_employer'] = vacancy_employer
            vacancy_data['vacancy_link'] = vacancy_link
            vacancy_data['vacancy_salary'] = vacancy_salary_data
            vacancies_list.append(vacancy_data)
    return vacancies_list

data = data_collect(max_page)

# Сохр в json
def data_to_json(data):
    with open(f'{keyword}.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


data_to_json(data)