import string
import numpy as np

import pandas as pd

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


def activate_checkbox(browser, input_xpath, clickable_xpath):
    input_element = browser.find_element_by_xpath(input_xpath)
    if not input_element.get_attribute('checked'):
        div = browser.find_element_by_xpath(clickable_xpath)
        div.click()


def get_table(browser):
    selector = '//div[@class="Flights-Results-React-FlexMatrixCollapsibleContainer-container"]//div[@role="grid"]'

    table_content = [row.text for row in browser.find_elements_by_xpath(selector + '//li[@role="gridcell"]/div[4]')]
    columns = [el.text for el in browser.find_elements_by_xpath(selector + '/div/ul[@role="row"]/li/div[1]')]
    index = [el.text for el in browser.find_elements_by_xpath(selector + '/div/ul[@role="grid"]/li/div[1]')]

    n = len(browser.find_elements_by_xpath(selector + '/div/div/ul[@role="row"]'))
    m = len(table_content) // n
    return pd.DataFrame([table_content[m*i:m*(i+1)] for i in range(n)], columns=columns, index=index)


def get_best_deals(browser, browser_wait, file_name="best_offers.png"):
    offer_xpath = '//div[@class="best-flights-list-results"]'
    element_present = EC.presence_of_element_located((By.XPATH, offer_xpath))
    browser_wait.until(element_present)
    browser.find_element_by_xpath(offer_xpath).screenshot(file_name)
    return file_name


# Price extraction
def extract_price(price_text):
    value = ''.join(c for c in price_text if c in string.digits)
    return float(value) if value else np.nan


def extract_price_from_element(browser, element_xpath):
    price_text = browser.find_element_by_xpath(element_xpath).text
    return extract_price(price_text)
