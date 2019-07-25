from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time


def rainsOpen():
    driver = webdriver.Chrome()  # Chromeを開く
    driver.get('https://system.reins.jp/reins/ktgyoumu/KG001_001.do')  # Rainsを開く
    time.sleep(20)  # ここでパス入力&ログインしてもらう
    chintai = driver.find_element_by_xpath(
        "/html/body/table[2]/tbody/tr/td[1]/div[3]/div[2]/form")  # 賃貸パス
    chintai.submit()
