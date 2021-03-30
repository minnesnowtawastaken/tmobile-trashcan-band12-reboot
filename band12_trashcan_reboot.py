import requests
import json
import os
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

if os.getenv('USERNAME') == None:
    username = 'admin'
else:
    username = os.getenv('USERNAME')

if os.getenv('PASSWORD') == None:
    print("Please supply a password")
    exit(1)

password = os.getenv('PASSWORD')

if os.getenv('RETRIES') == None:
    retries = 12
else:
    retries = int(os.getenv('RETRIES'))

page = requests.get('http://192.168.12.1/fastmile_radio_status_web_app.cgi').content


def reboot_modem():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome('/usr/local/bin/chromedriver', options=options)
    driver.get('http://192.168.12.1/web_whw/#/overview')
    driver.find_element_by_xpath('/html/body/app-root/app-side-menu/mat-sidenav-container/mat-sidenav/div/mat-nav-list/app-menu[5]/div/a').click()
    driver.find_element_by_xpath('//*[@id="login-dialog-name-placeholder"]').send_keys(username)
    driver.find_element_by_xpath('//*[@id="login-dialog-pass-placeholder"]').send_keys(password)
    driver.find_element_by_xpath('//*[@id="login-dialog-button-login"]').click()
    time.sleep(3)
    driver.find_element_by_xpath('//*[@id="restart"]').click()
    driver.find_element_by_xpath('//*[@id="mat-dialog-1"]/app-confirm-dialog/div[3]/button[2]').click()
    time.sleep(3)
    driver.quit()


def check_band_again():
    try:
        while requests.get('http://192.168.12.1/fastmile_radio_status_web_app.cgi').status_code != 200:
            time.sleep(10)
        # after the modem comes up, wait 20 seconds for the bands to stabilize if needed
        time.sleep(20)
        page = requests.get('http://192.168.12.1/fastmile_radio_status_web_app.cgi').content
        if json.loads(page)['cell_LTE_stats_cfg'][0]['stat']['Band'] == 'B12':
            print("Band 12 still detected, rebooting again")
            return False
        else:
            print("Band 12 not detected - exiting")
            return True
    except requests.exceptions.ConnectionError:
        time.sleep(5)
        check_band_again()


if json.loads(page)['cell_LTE_stats_cfg'][0]['stat']['Band'] == 'B12':
    print("Band 12 detected, rebooting")
    retries_iter = 0
    while retries_iter < retries:
        reboot_modem()
        # let modem settle - seems to always pick b12 at first
        print("Reboot kicked off, sleeping for 10 minutes")
        time.sleep(600)
        if check_band_again():
            break
        else:
            retries_iter += 1
else:
    print("Band 12 not detected, exiting")

