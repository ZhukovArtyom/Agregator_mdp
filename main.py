from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from Text_analizer import TextRazorTextAnalyzer
import pandas as pd


chrome_options = Options()
chrome_options.add_argument("--headless")
browser = webdriver.Chrome(options=chrome_options)
analyzer = TextRazorTextAnalyzer(api_key='a90dfa9be138cd3d10594dec6e88d915d6c84b8337a338f81db3b807')


pages_for_analyse=1
# Словарь для хранения данных
data = []

# Функция для добавления данных в список
def add_news_to_data(university, header, image, date, link, categories):
    if categories:
        for category in categories:
            data.append({"Университет": university, "Заголовок": header,
                         "Изображение": image, "Дата": date, "Ссылка": link, "Категория": category,})

# Обработка новостей для Ярославского педагогического университета
ped_page = 'https://news.yspu.org/cat/news'
browser.get(ped_page)
count = 0
while count < pages_for_analyse:
    num = 0

    WebDriverWait(browser, 10).until(
        expected_conditions.presence_of_all_elements_located((By.CLASS_NAME, "entry-title")))

    block = browser.find_elements(by="class name", value="entry-title")
    while num < len(block):
        block = browser.find_elements(by="class name", value="entry-title")
        news_header = block[num].find_element(by='css selector', value='a')
        header_text = news_header.text
        link = news_header.get_attribute(name="href")
        browser.get(link)

        WebDriverWait(browser, 10).until(
            expected_conditions.presence_of_element_located((By.CLASS_NAME, "entry-content")))

        text = browser.find_element(by="class name", value="entry-content").text

        try:
            image = browser.find_element(by="class name", value="wp-post-image").get_attribute(name="src")
        except NoSuchElementException:
            image = "no_img"

        date = browser.find_element(by="class name", value="entry-date").text
        categories = analyzer.analyze_text(text)
        add_news_to_data("Ярославский педагогический университет", header_text, image, date, link, categories)
        browser.back()
        num += 1

    WebDriverWait(browser, 10).until(
        expected_conditions.presence_of_all_elements_located((By.CLASS_NAME, "page-numbers")))

    arrows = browser.find_elements(by="class name", value="page-numbers")
    if arrows[-1].text == "Следующий":
        browser.get(arrows[-1].get_attribute(name="href"))
        count += 1
    else:
        count = 0
        break

# Обработка новостей для ЯрГУ им. П.Г. Демидова
dem_page = 'https://www.uniyar.ac.ru/news/main1443000'
browser.get(dem_page)
count = 0
while count < pages_for_analyse:
    num = 0

    WebDriverWait(browser, 10).until(
        expected_conditions.presence_of_all_elements_located((By.CLASS_NAME, "news-item-header")))

    block = browser.find_elements(by="class name", value="news-item-header")
    while num < len(block):
        block = browser.find_elements(by="class name", value="news-item-header")
        news_header = block[num].find_element(by='css selector', value='a')
        header_text = news_header.text
        link = news_header.get_attribute(name="href")
        browser.get(link)

        WebDriverWait(browser, 10).until(
            expected_conditions.presence_of_element_located((By.CLASS_NAME, "news-item-text")))

        text = browser.find_element(by="class name", value="news-item-text").text

        try:
            image_box = browser.find_element(by="class name", value="news-item-image")
            image = image_box.find_element(by="css selector", value="img").get_attribute(name="src")
        except NoSuchElementException:
            image = "no_img"

        date = browser.find_element(by="class name", value="b-news__date").text
        categories = analyzer.analyze_text(text)
        add_news_to_data("ЯрГУ им. П.Г. Демидова", header_text, image, date, link, categories)
        browser.back()
        num += 1

    WebDriverWait(browser, 10).until(
        expected_conditions.presence_of_all_elements_located((By.CLASS_NAME, "b-paging__arrow")))
    arrows = browser.find_elements(by="class name", value="b-paging__arrow")
    if arrows[-1].get_attribute(name="title") == "След.":
        browser.get(arrows[-1].get_attribute(name="href"))
        count += 1
    else:
        count = 0
        break

# Обработка новостей для ЯГТУ
ystu_page = 'https://www.ystu.ru/news'
browser.get(ystu_page)
count = 0
while count < pages_for_analyse:
    num = 0

    WebDriverWait(browser, 10).until(
        expected_conditions.presence_of_all_elements_located((By.CLASS_NAME, "news-item--page")))

    block = browser.find_elements(by="class name", value="news-item--page")
    while num < len(block):
        block = browser.find_elements(by="class name", value="news-item--page")
        one_block = block[num]
        news_header = one_block.find_element(by='class name', value='news-item__title')
        header_text = news_header.text
        link = one_block.get_attribute(name="href")
        browser.get(link)

        WebDriverWait(browser, 10).until(
            expected_conditions.presence_of_all_elements_located((By.CLASS_NAME, "page-main-content-news__description")))

        texts = browser.find_elements(by="class name", value="page-main-content-news__description")
        text = " ".join([t.text for t in texts])
        content_box = browser.find_element(by="class name", value="page-main-content-news")

        try:
            image = content_box.find_element(by="css selector", value="img").get_attribute("src")
        except NoSuchElementException:
            image = "no_img"

        date = content_box.find_element(by="class name", value="page-main-content-news__date").text
        categories = analyzer.analyze_text(text)
        add_news_to_data("ЯГТУ", header_text, image, date, link, categories)
        browser.back()
        num += 1

    WebDriverWait(browser, 10).until(
        expected_conditions.presence_of_all_elements_located((By.CSS_SELECTOR, "font")))

    main_cont = browser.find_element(by="class name", value="page-main")
    fonts = main_cont.find_elements(by="css selector", value="font")
    arrows = fonts[-1].find_elements(by="css selector", value="a")
    if arrows[-2].text == "След.":
        browser.get(arrows[-2].get_attribute(name="href"))
        count += 1
    else:
        count = 0
        break

# Сохранение данных в CSV файл
df = pd.DataFrame(data)
df.to_csv('news_categories.csv', index=False, sep=',', encoding='utf-8-sig')


print("Данные успешно сохранены в файл news_categories.csv.")







