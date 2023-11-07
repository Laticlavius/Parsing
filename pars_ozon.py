from selenium import webdriver
from selenium_stealth import stealth
import seleniumbase as sb
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
import time
from bs4 import BeautifulSoup as bs
import re
import pandas as pd
import os
import warnings

warnings.filterwarnings('ignore')


class Parse:
    def __init__(self, keyword):
        self.keyword = keyword
        self.url = "https://www.ozon.ru/"

        self.driver = sb.Driver(browser='chrome', headless=False, uc=True)
        self.wait = webdriver.Chrome.implicitly_wait(self.driver, 500.00)
        self.filename = 'result.csv'
        self.filepath = os.path.join(os.getcwd(), self.filename)
        self.link = 'https://www.ozon.ru'

        stealth(
            driver=self.driver,
            languages=["ru-Ru", "ru"],
            vendor="Google Inc.",
            platform="Win64",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
            wait=self.wait
        )
    def has_russian_chars(self, string):
        pattern = re.compile("[а-яА-ЯёЁ]")
        return bool(pattern.search(string))

    def write_to_csv(self, html):
        soup = bs(html, 'html.parser')
        ds = pd.DataFrame(columns = ['Brand','Name', 'Url', 'About_the_product', 'Rating', 'Number_of_reviews'])
        parent_div = soup.find_all('div', class_='i9u')

        for i in parent_div:
            result = {}
            # Получаем брен производителя
            brand = i.find('div', class_='tsBodyM')
            if brand is None:
                brand = ' '
            else:
                brand = brand.text
                if self.has_russian_chars(brand):
                    brand = ' '
            # Получаем ссыдку на товар в маркетплейсе
            url = i.find('a', class_='ri9').get('href')
            url = self.link + url
            # Получаем название товара
            name = (i.find('span', class_='tsBody500Medium').text).strip()
            name = re.sub(r'\s+',' ', name)
            # Получаем словарь с описанием товара
            text = i.find('span', class_='tsBody400Small')
            for font in text.find_all('font'):
                key =  re.sub(" +", " ",font.previous_sibling.strip(':')) 
                key = (key).replace('\n', ' ').strip()
                value = (font.text).replace('\n', ' ').strip()
                result[key] = value
            # Получаем рейтинг и количество отзывов
            rat_and_raw = i.find('div', class_='tsBodyMBold')
            if rat_and_raw is None:
                rating = 0.0
                num_reviews = 0
            else:
                rat_and_raw = rat_and_raw.text
                rat_and_raw = (re.sub(r'\s+',' ', rat_and_raw)).split(' ')
                rating = rat_and_raw[0]
                num_reviews = rat_and_raw[1]
            ds = ds._append({'Brand':brand, 'Name': name, 'Url': url,'About_the_product': result, 'Rating': rating, 'Number_of_reviews': num_reviews}, ignore_index=True)


        if os.path.exists(self.filepath):
            ds.to_csv(self.filename, mode='a', index=False, header=False)
        else:
            ds.to_csv('result.csv')

    def run(self):
        try:
            self.driver.get(self.url)
            input = self.driver.find_element(By.XPATH,("//input[@placeholder='Искать на Ozon']"))
            input.click()
            input.send_keys(self.keyword)
            find_button = self.driver.find_element(By.CSS_SELECTOR,(".a2429-a4.a2429-a3"))
            find_button.click()
            time.sleep(10)
            flag = True
            while flag:
                try:
                    for _ in range(30):
                        self.driver.execute_script('window.scrollBy(0, 300);')
                        time.sleep(.5)


                    time.sleep(5)
                    element = WebDriverWait(self.driver, 10).until(
                        ec.presence_of_element_located((By.ID, "ozonTagManagerApp")))
                    try:
                        self.write_to_csv(self.driver.page_source)
                        element_next = self.driver.find_element(By.XPATH,('//div[contains(text(), "Дальше")]'))
                        time.sleep(1)
                        element_next.click()
                    except NoSuchElementException:
                        flag = False
                finally:
                    # self.write_to_csv(self.driver.page_source)
                    # return self.driver.page_source
                    time.sleep(5)
        except Exception as ex:
            print(ex)
        finally:
            self.driver.close()
            self.driver.quit()


if __name__ == "__main__":
    Parse('Видеокарта 3060').run()
    



