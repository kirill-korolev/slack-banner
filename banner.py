#!/usr/bin/env python

import time
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys

class Banner:
    URL = "https://bitclaveio.slack.com/admin?range="
    LOGIN = 'kafafyf@gmail.com'
    PASSWORD = 'kafafyf2016'

    RANGES = [('A', 'C'), ('D', 'F'), ('G', 'I'), ('J', 'L'), ('M', 'O'), ('P', 'R'), ('S', 'U'), ('V', 'Z'), ('0', '9')]

    def __init__(self):
        pass

    def _find_tuple(self, nickname: str):

        for range in Banner.RANGES:
            f, s = range
            if f.lower() <= nickname[0].lower() <= s.lower():
                return range

    def ban(self, nickname: str):
        try:
            print("Starting to ban {0}".format(nickname))


            desired_cap = {'os': 'Windows', 'os_version': '10', 'browser': 'firefox', 'browser_version': '32.0'}

            driver = webdriver.Remote(
                command_executor='http://kirillkorolev1:LY1yfs1SXqqsujCuRzoQ@hub.browserstack.com:80/wd/hub',
                desired_capabilities=desired_cap)

            driver.maximize_window()

            tuple = self._find_tuple(nickname)
            driver.get("{0}{1}-{2}".format(Banner.URL, *tuple))

            email = driver.find_element_by_css_selector('#email')
            password = driver.find_element_by_css_selector('#password')
            button = driver.find_element_by_css_selector('#signin_btn')

            email.send_keys(Banner.LOGIN)
            password.send_keys(Banner.PASSWORD)

            button.click()

            print("Entering an email and a password...")

            search = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.member_filter'))
            )

            search.send_keys(nickname, Keys.ENTER)
            print("Searching...")
            time.sleep(2)

            pop_up = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.admin_list_item'))
            )
            pop_up.click()

            print("Pop-up...")
            #time.sleep(2)


            disable = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, '.api_disable_account'))
            )

            print("Enabled: %s" % disable.is_enabled())
            print("Displayed: %s" % disable.is_displayed())

            actions = webdriver.ActionChains(driver)
            actions.move_to_element(disable)
            actions.click(disable)
            actions.perform()

            time.sleep(3)
            print("{0} was banned!".format(nickname))

            return True
        except Exception as exc:
            print("Error during banning: {0}".format(exc))
            return False
        finally:
            driver.quit()