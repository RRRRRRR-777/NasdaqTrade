from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
import os
from bs4 import BeautifulSoup
import codecs
import shutil
import selenium
import pandas as pd
import time
import glob
import numpy as np
from lxml import etree


#実行時間の計測
start = time.time()

# 銘柄のリストを読み込む
input_df = pd.read_csv(os.getcwd()+"/Stock_Trade/Comprehensive.csv")["Ticker"]

# リスト型のデータ変数
data = []
error_data = []

# flg
add_error_flg = True

# スクリーンショットを保存
shutil.rmtree(os.getcwd()+"/selenium_screen_shot")
os.mkdir(os.getcwd()+"/selenium_screen_shot")

# 対象リンク
loggin_url = "https://whalewisdom.com/dashboard2/search/stock_screener"

# WEBブラウザの起動
chromedriver = os.getcwd() + "/driver/chromedriver"

#ドライバの設定
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument("--no-sandbox")
options.add_argument('--disable-gpu') # これが勝因かもしれない headlessではログインできなかった
options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.105 Safari/537.36')
options.add_argument('--user-data-dir=~/Library/Application Support/Google/Chrome')
options.add_argument('--profile-directory=Profile1') # recapcahエラーの際にユーザーを変えたらログインできた
# Chromeのユーザーとしてrecapchaのブロックを食らっていた可能性、または時間をおいたからログインできたのかも←多分後者
driver = webdriver.Chrome(chromedriver, chrome_options=options)
driver.set_window_size(1200, 1000)

data = []

try:
    # サイトにログインする
    driver.get(loggin_url) # URLを開く

    driver.implicitly_wait(1.0)
    driver.find_element(By.XPATH, '//*[@id="stock-screener-page"]/div[3]/div/div[2]/div[1]/div/div/div/div[1]/div[2]/div/i').click()
    driver.implicitly_wait(1.0)
    driver.find_element(By.XPATH, '//*[@id="list-item-1089-3"]/div/div').click()

    sleep(2.0)
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, "html.parser")

    driver.implicitly_wait(1.0)
    tr = soup.find("tbody").find_all("tr")

    for row in tr:
        td = row.find_all("td")
        ticker = td[2].text.replace("\n", "").replace(" ", "")
        perf_inst = td[17].text.replace("\n", "").replace(" ", "")
        data.append([ticker, perf_inst])

    print(data)

except Exception as e:
    print(f"________________ERROR________________\n{e}")
    pass


# ドライバーを終了する
driver.close()



# width = driver.execute_script("return document.body.scrollWidth;")
# height = driver.execute_script("return document.body.scrollHeight;")
# driver.set_window_size(width,height)
# driver.save_screenshot("selenium_screen_shot/00.png") # ?

# ! 500銘柄までだったので元の方法でやり直す！