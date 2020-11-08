import os
import time
import yaml
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains

from selenium.common.exceptions import TimeoutException

from webdriver_manager.firefox import GeckoDriverManager

from Dmail.esp import Hotmail

import extended_expected_conditions as EEC
from utilities import extract_price_from_element, activate_checkbox
from utilities import get_table, get_best_deals
from email_utilities import get_message


# Options
departure = 'Paris'
arrival = 'Tunis'
max_price = 950

# Personal information
username = 'YOUR_NAME'
email = 'SENDER_EMAIL@hotmail.fr'
recipient_email = 'RECIPIENT_MAIL@domain.com'
password = 'YOUR_PASSWORD'


browser = webdriver.Firefox(executable_path=GeckoDriverManager().install())
browser.implicitly_wait(10)
browser_wait = WebDriverWait(browser, 30)

browser.get("https://www.kayak.com/flights")

# Go to Flights
with open('search_page.yaml', 'r') as f:
    search_page_selectors = yaml.load(f, Loader=yaml.SafeLoader)

time.sleep(1)
try:
    cookies_xpath = search_page_selectors['accept_cookies_xpath']
    WebDriverWait(browser, 5).until(EC.element_to_be_clickable((By.XPATH, cookies_xpath))).click()
except TimeoutException:
    pass

time.sleep(1)

browser.find_element_by_xpath(search_page_selectors['from_click_xpath']).click()
browser.find_element_by_xpath(search_page_selectors['from_text_xpath']).send_keys(Keys.BACKSPACE + Keys.BACKSPACE + departure)
time.sleep(0.5)
browser.find_element_by_xpath(search_page_selectors['from_text_xpath']).send_keys(Keys.RETURN)
time.sleep(1)

# To
browser.find_element_by_xpath(search_page_selectors['to_click_xpath']).click()
browser.find_element_by_xpath(search_page_selectors['to_text_xpath']).send_keys(arrival)
time.sleep(0.5)
browser.find_element_by_xpath(search_page_selectors['to_text_xpath']).send_keys(Keys.RETURN)
time.sleep(1)

# From Date
browser.find_element_by_xpath(search_page_selectors['date_picker_from_xpath']).click()
time.sleep(1)
Select(browser.find_element_by_xpath(search_page_selectors['from_flexible_xpath'])).select_by_value('plusminusthree')
Select(browser.find_element_by_xpath(search_page_selectors['to_flexible_xpath'])).select_by_value('plusminusthree')


browser.find_element_by_xpath(search_page_selectors['from_date_click_xpath']).click()
browser.find_element_by_xpath(search_page_selectors['from_date_text_xpath']).clear()
browser.find_element_by_xpath(search_page_selectors['from_date_text_xpath']).send_keys('05/08/2021')
time.sleep(1)
browser.find_element_by_xpath(search_page_selectors['to_date_text_xpath']).clear()
time.sleep(1)
browser.find_element_by_xpath(search_page_selectors['to_date_text_xpath']).send_keys('13/08/2021')
time.sleep(1)
browser.find_element_by_xpath(search_page_selectors['submit_button_xpath']).click()


# Page 2
with open('results_page.yaml', 'r') as f:
    results_page_selectors = yaml.load(f, Loader=yaml.SafeLoader)

browser_wait.until(EEC.progressbar_is_full((By.XPATH, results_page_selectors['progressbar_xpath'])))

for el in browser.find_elements_by_xpath(results_page_selectors['close_alert_xpath']):
    if el.is_displayed():
        el.click()

if not browser.find_element_by_xpath(results_page_selectors['price_slider_xpath']).is_displayed():
    browser_wait.until(EC.element_to_be_clickable((By.XPATH, results_page_selectors['price_toggle_xpath']))).click()

# select slider
slider = browser.find_element_by_xpath(results_page_selectors['price_slider_xpath'])

# scroll to make the slider visible on screen
browser.execute_script("arguments[0].scrollIntoView(false);", slider)

# Defining Actions chains
browser_move = ActionChains(browser)
browser_move.click_and_hold(slider).move_by_offset(-5, 0).release()

# Moving slider to select price range
if extract_price_from_element(browser, results_page_selectors['min_price_xpath']) <= max_price:
    while extract_price_from_element(browser, results_page_selectors['max_price_xpath']) > max_price:
        browser_move.perform()


# Activate flexible modifications checkbox
activate_checkbox(browser, results_page_selectors['flexible_modifications_xpath'],
                  results_page_selectors['flexible_modifications_click_xpath'])

# Activate flexible refund checkbox
activate_checkbox(browser, results_page_selectors['flexible_refund_xpath'],
                  results_page_selectors['flexible_refund_click_xpath'])


time.sleep(3)

table = get_table(browser)
filename = get_best_deals(browser, browser_wait)

# Creating the email body
message = get_message(user=username, screenshot_path=filename, table=table)

# Sending the email
with Hotmail(email, password) as email:
    email.send(message, recipient_email,
               subject=f"[Kayak] Best flight deals on the {datetime.now():%Y-%m-%d}")
