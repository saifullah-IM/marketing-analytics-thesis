"""
dependencies:
    python 3
    selenium 4
    webdriver_manager 3
    flask 2
    flask-restful
"""

import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from flask import Flask
from flask_restful import Api, Resource

# from selenium.webdriver.support.wait import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.keys import Keys


def to_number(num_str):
    num = ""
    for ch in num_str:
        if ch.isdigit():
            num += ch
        elif ch == '.':
            num += ch
    return float(num)


def found_in_name(name, query):
    for word in query.split():
        if word not in name:
            return False
    else:
        return True


# def write_json(scrapped_data, filename):
#     with open(filename, 'w') as file:
#         json.dump(scrapped_data, file)


class ChaldalScrapper:
    def __init__(self):
        pass

    def generate_link(self, query):
        link = "https://chaldal.com/search/"
        link += '%20'.join(query.split())
        return link

    def scrape(self, query="", filter=False):
        link = self.generate_link(query)

        chrome_options = Options()
        chrome_options.add_argument("--headless")

        driver = webdriver.Chrome(options=chrome_options, service=Service(ChromeDriverManager().install()))
        driver.get(link)
        time.sleep(5)

        products = driver.find_elements(By.XPATH, "//div[@class='product']")
        scrapped_data = []
        # print(len(products))

        for product in products:
            name = product.find_element(By.XPATH, ".//div[@class='name']").text

            price_elements = product.find_elements(By.XPATH, ".//div[@class='price']//span")
            original_price = price_elements[1].text

            discounted_price_elements = product.find_elements(By.XPATH, ".//div[@class='discountedPrice']//span")
            if len(discounted_price_elements) == 0:
                discounted_price = original_price
            else:
                discounted_price = discounted_price_elements[1].text

            quantity = product.find_element(By.XPATH, ".//div[@class='subText']").text

            link = product.find_element(By.XPATH, ".//a").get_attribute('href')

            original_price = to_number(original_price)
            discounted_price = to_number(discounted_price)
            discount = self.calc_discount(original_price, discounted_price)

            if filter and not found_in_name(name.lower(), query.lower()):
                continue

            product_data = {"name": name,
                            "originalPrice": original_price,
                            "discountedPrice": discounted_price,
                            "discountPercentage": discount,
                            "quantity": quantity,
                            "url": link
                            }
            # print(product_data)
            scrapped_data.append(product_data)

        driver.close()
        return json.dumps(scrapped_data)

    def calc_discount(self, original_price, discounted_price):
        discount = ((original_price - discounted_price) / original_price) * 100
        discount = round(discount, 2)
        return discount


class DarazScrapper:
    def __init__(self):
        pass

    def generate_link(self, query):
        link = "https://www.daraz.com.bd/catalog/?q="
        link += '+'.join(query.split())
        return link

    def scrape(self, query="", filter=False):
        link = self.generate_link(query)

        chrome_options = Options()
        chrome_options.add_argument("--headless")

        driver = webdriver.Chrome(options=chrome_options, service=Service(ChromeDriverManager().install()))
        driver.get(link)
        time.sleep(5)

        products = driver.find_elements(By.XPATH, "//div[@data-qa-locator='product-item']")
        scrapped_data = []
        # print(len(products))

        for product in products:
            a_elements = product.find_elements(By.XPATH, ".//a")
            name = a_elements[1].get_attribute('title')
            link = a_elements[1].get_attribute('href')

            discounted_price = product.find_element(By.XPATH, ".//div[@class='price--NVB62']//span").text

            price_elements = product.find_elements(By.XPATH, ".//del")
            if len(price_elements) == 0:
                original_price = discounted_price
            else:
                original_price = price_elements[0].text

            discount_elements = product.find_elements(By.XPATH, ".//span[@class='discount--HADrg']")
            if len(discount_elements) == 0:
                discount = '-0%'
            else:
                discount = discount_elements[0].text

            discounted_price = to_number(discounted_price)
            original_price = to_number(original_price)
            discount = to_number(discount)

            if filter and not found_in_name(name.lower(), query.lower()):
                continue

            product_data = {"name": name,
                            "originalPrice": original_price,
                            "discountedPrice": discounted_price,
                            "discountPercentage": discount,
                            "quantity": "",
                            "url": link
                            }
            # print(product_data)
            scrapped_data.append(product_data)

        driver.close()
        return json.dumps(scrapped_data)


# def run_scrapper(query):
#     chaldal_scrapper = ChaldalScrapper()
#     chaldal_data = chaldal_scrapper.scrape(query, True)
#     print(chaldal_data)
#     # write_json(chaldal_data, query + '_chaldal_data' + '.json')
#
#     daraz_scrapper = DarazScrapper()
#     daraz_data = daraz_scrapper.scrape(query, True)
#     print(daraz_data)
#     # write_json(daraz_data, query + '_daraz_data' + '.json')


app = Flask(__name__)
api = Api(app)


class ScrapeData(Resource):
    def get(self, site, search_query):
        data = {}
        site = site.lower()
        if site == "chaldal":
            scrapper = ChaldalScrapper()
            data = scrapper.scrape(search_query, True)
        elif site == "daraz":
            scrapper = DarazScrapper()
            data = scrapper.scrape(search_query, True)
        return data


api.add_resource(ScrapeData, "/search/<string:site>/<string:search_query>")


if __name__ == "__main__":
    # run_scrapper("Sunsilk stunning black shine")
    # app.run(debug=True)
    app.run()
