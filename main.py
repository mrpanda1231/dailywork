import os
import sys
import time
import datetime
import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC

import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M',
                    handlers=[logging.FileHandler('.log', 'a', 'utf-8'), ])

"""
Function description:
Send message through http request to telegram; Datetime will be added on the message

Inpout:
msg: str, the message you wwant to deliever
"""


def send_tg(msg):
    base_url = 'https://api.telegram.org/bot%s/sendMessage?chat_id=%s&text=' % (tg_token, tg_chat_id) + \
               datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S : ")
    requests.get(base_url + msg)
    return


url = "https://www.services.gov.on.ca/sf/#/oneServiceDetail/137/ab/12043"
email = "abctesting@gmail.com"
first_name = "Peter"
last_name = "Chu"
tg_token = ''
tg_chat_id = ''
tel = 1234567890

if __name__ == '__main__':
    print('Start monitor.')

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    browser = webdriver.Chrome('chromedriver.exe', options=options)

    browser.get(url)

    # Store the last request; It is used for comparing the current result. If they are the same, then ignore the result.
    last_result = []

    while True:

        try:
            WebDriverWait(browser, 60).until(EC.visibility_of_element_located((By.NAME, "FirstName")))

            """
            Usually, below info should be entered if you submit the registration info.
                        
            But When language section is selected, the option will prompt automatically. 
            Thus no need to enter below info.
            """
            # browser.find_element(By.NAME, "FirstName").send_keys(first_name)
            # browser.find_element(By.NAME, "LastName").send_keys('last_name')
            # browser.find_element(By.NAME, "EmailAdress").send_keys(email)
            # browser.find_element(By.NAME, "ReEmail").send_keys(email)
            # browser.find_element(By.NAME, "Phone").send_keys(tel)
            select = Select(browser.find_element(By.NAME, "Lang"))
            select.select_by_visible_text('English')

            # Wait until "BookDate" element prompt out
            WebDriverWait(browser, 180).until(EC.visibility_of_element_located((By.NAME, "BookDate")))

            bookDate = browser.find_element(By.NAME, "BookDate")
            options = bookDate.find_elements_by_tag_name('option')

            if len(options) == 1:
                if options[0].text == 'Please select a day':
                    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S : "), 'No selection')
                    logging.info('No selection')
                else:
                    msg = options[0].text
                    send_tg(msg)
                    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S : "), msg)
                    logging.info(msg)
            else:
                """
                selections: list, store the option date
                selections_tg: list, store the option date in format '%A, %B %d, %Y', for telegram use
                send_tg_str: list, screen items in selections_tg and store   
                """
                selections = []
                selections_tg = []
                send_tg_str = []

                for i in options:
                    date_str = i.text

                    if date_str == 'Please select a day':
                        continue

                    selections.append(date_str)

                    date_dt = datetime.datetime.strptime(date_str, '%A, %B %d, %Y')
                    selections_tg.append(date_dt)

                for item in selections_tg:
                    # If the date is not with two weeks, it will be ignored.
                    if datetime.datetime.now() + datetime.timedelta(days=14) <= item:
                        continue
                    send_tg_str.append(item.strftime('%b-%d'))

                # for log
                msg = ','.join(selections)
                logging.info(msg)

                # Sending tg
                if len(send_tg_str) > 0:
                    if selections != last_result:
                        last_result = selections
                    msg = ','.join(send_tg_str)
                    send_tg(msg)
                    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S : "), msg)
                else:
                    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S : "), 'date options out of range')
        except Exception as e:
            print('Error %s' % e)

        browser.close()

        time.sleep(2*60)
